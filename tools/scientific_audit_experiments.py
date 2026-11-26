#!/usr/bin/env python3
"""Deterministic audit experiments. No changes to application null models.

Run from any directory. Outputs are generated data, separate from the GUI.
Only Python's standard library and NumPy are needed.
"""
import argparse
import csv
from dataclasses import asdict,replace
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from app_config import config_dict,reset_config
from atlas_engine import (GridConfig,PLACEMENTS,build_volume,
    projection,overlay_metrics,placement_geometry_metrics,_base_and_step,clear_volume_cache)
from compute_backend import configure_backend
from metrics import prime_grid_metrics,fft2_structure_metrics,random_baseline_metrics_for_hits

KEYS=('alive_density','local_entropy_mean','global_entropy','edge_density',
      'fft_peak_ratio','fft_axis_ratio','fft_lowfreq_ratio','fft_spectral_entropy','beauty_score')


def measure(a,binary=True):
    a=np.asarray(a)
    h,w=a.shape
    m=prime_grid_metrics(a,np.arange(1,a.size+1),w,h,a.size)
    if not binary: m.update(fft2_structure_metrics(a,w,h,binary=False))
    return {k:m[k] for k in KEYS}


def write_csv(output,name,rows):
    rows=list(rows)
    with (output/name).open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def run(output,trials,seed,replicates):
    reset_config();configure_backend('CPU')
    output.mkdir(parents=True,exist_ok=True)
    y,x=np.indices((24,24))
    patterns={
        'all_zeros':np.zeros((24,24),int),
        'all_ones':np.ones((24,24),int),
        'single_point':((x==12)&(y==12)).astype(int),
        'checkerboard':(x+y)%2,
        'vertical_stripes':(x%4<2).astype(int),
        'horizontal_stripes':(y%4<2).astype(int),
        'diagonal_stripes':((x+y)%4<2).astype(int),
        'random_Bernoulli':(np.random.default_rng(seed).random((24,24))<.3).astype(int),
        # Integer-valued periodic sinusoid: meaningful scalar field also for
        # hit entropy/beauty, without silently truncating fractional hits.
        'periodic_sinusoid':np.tile([2,3,2,1],(24,6)),
        'single_line':(x==12).astype(int),
    }
    synthetic=[]
    for name,a in patterns.items():
        synthetic.append({'pattern':name,'FFT_input':'scalar' if name=='periodic_sinusoid' else 'binary',**measure(a,name!='periodic_sinusoid')})
    write_csv(output,'synthetic_metrics.csv',synthetic)
    print('Synthetic metrics complete',flush=True)

    # The uniform null below is the application's exact current generator.
    cfg=GridConfig(30,30,2,start=1001)
    data=projection(cfg,overlay=True)
    base,step=_base_and_step(data,'XY',cfg)
    hits=data['hits'].ravel();positive=hits[hits>0];alive_count=len(positive)
    allowed=np.flatnonzero(np.gcd(base,step)==1)
    assert not np.any((hits>0)&(np.gcd(base,step)!=1)), 'Choose a range without prime divisors of M'
    observed=prime_grid_metrics(hits,base,cfg.x,cfg.y,step)
    coprime=prime_grid_metrics((np.gcd(base,step)==1).astype(int),base,cfg.x,cfg.y,step)
    write_csv(output,'null_controls.csv',[{'control':name,**{k:m[k] for k in KEYS}} for name,m in [('prime',observed),('coprime_mask',coprime)]])
    all_null=[];summary=[]
    for model in ['uniform_resampled','coprime_conditioned_resampled','coprime_conditioned_exact_hits']:
        rng=np.random.default_rng(seed)
        pool=np.arange(hits.size) if model.startswith('uniform') else allowed
        rows=[]
        for trial in range(trials):
            sample=np.zeros(hits.size,dtype=np.int32)
            positions=rng.choice(pool,size=alive_count,replace=False)
            values=rng.permutation(positive) if model.endswith('exact_hits') else rng.choice(positive,size=alive_count,replace=True)
            sample[positions]=values
            m=prime_grid_metrics(sample,base,cfg.x,cfg.y,step)
            rows.append({'model':model,'trial':trial,**{k:m[k] for k in KEYS}})
        all_null.extend(rows)
        if model=='uniform_resampled':
            app_mean=random_baseline_metrics_for_hits(hits,base,cfg.x,cfg.y,step,trials=trials,seed=seed)
            for k in KEYS: np.testing.assert_allclose(np.mean([r[k] for r in rows]),app_mean[k],rtol=1e-12,atol=1e-12)
        for k in KEYS:
            vals=np.array([r[k] for r in rows]);v=observed[k]
            # Relative equality avoids labelling roundoff as order evidence.
            ties=np.isclose(vals,v,rtol=1e-12,atol=1e-12)
            less=(vals<v)&~ties;greater=(vals>v)&~ties
            summary.append({'model':model,'metric':k,'observed':v,
                'mean':float(vals.mean()),'sd':float(vals.std(ddof=1)),
                'q025':float(np.quantile(vals,.025)),'q975':float(np.quantile(vals,.975)),
                'percentile_midrank':float(100*(less.sum()+.5*ties.sum())/trials),
                'upper_tail_fraction':float((greater|ties).mean()),
                'lower_tail_fraction':float((less|ties).mean()),
                'trial_count':trials})
    write_csv(output,'null_trials.csv',all_null)
    write_csv(output,'null_summary.csv',summary)
    print('Uniform and conditioned null trials complete',flush=True)

    density=[]
    for p in [.05,.10,.20,.30,.50]:
        for rep in range(replicates):
            # Matched random uniforms across p: comparisons are paired.
            rng=np.random.default_rng(seed+1000+rep)
            a=(rng.random((32,32))<p).astype(int)
            density.append({'target_density':p,'replicate':rep,**measure(a)})
    write_csv(output,'density_trials.csv',density)
    density_summary=[]
    for p in [.05,.10,.20,.30,.50]:
        rows=[r for r in density if r['target_density']==p]
        density_summary.append({'target_density':p,**{k:float(np.mean([r[k] for r in rows])) for k in KEYS}})
    write_csv(output,'density_summary.csv',density_summary)

    aspect=[]
    for rep in range(replicates):
        flat=(np.random.default_rng(seed+2000+rep).random(300)<.3).astype(int)
        a=flat.reshape(30,10);b=flat.reshape(20,15)
        for w,h,arr in [(10,30,a),(15,20,b),(20,15,b.T),(30,10,a.T)]:
            aspect.append({'X':w,'Y':h,'replicate':rep,**measure(arr)})
    write_csv(output,'aspect_trials.csv',aspect)
    write_csv(output,'aspect_summary.csv',[{'X':w,'Y':h,
        'isotropic_flat_power_axis_fraction':(w+h-2)/(w*h-1),
        **{k:float(np.mean([r[k] for r in aspect if r['X']==w])) for k in KEYS}}
        for w,h in [(10,30),(15,20),(20,15),(30,10)]])

    symmetry=[]
    yy,xx=np.indices((9,12))
    matrices={'periodic_diagonal_9x12':((xx+yy)%3==0).astype(int),
              'generic_binary_9x12':(np.random.default_rng(seed).random((9,12))<.3).astype(int)}
    for name,a in matrices.items():
        for trans,b in [('original',a),('transpose',a.T),('flip_x',np.fliplr(a)),('flip_y',np.flipud(a)),('rotate_90',np.rot90(a))]:
            m=measure(b)
            # Geometry only: beauty's fixed residue mask is intentionally not
            # co-transformed, so it has no expected symmetry here.
            m.pop('beauty_score')
            centered=b-b.mean();power=abs(np.fft.fftshift(np.fft.fft2(centered)))**2
            power[b.shape[0]//2,b.shape[1]//2]=0
            symmetry.append({'pattern':name,'transform':trans,'positive_power_bins':int((power>0).sum()),**m})
    write_csv(output,'symmetry_metrics.csv',symmetry)

    placements=[]
    reference=GridConfig(15,20,4,start=1001)
    for p in PLACEMENTS:
        cfgp=replace(reference,placement=p)
        nums,selected=build_volume(cfgp)
        assert np.array_equal(np.sort(nums.ravel()),np.arange(1001,2201))
        for plane in ['XY','XZ','YZ']:
            placements.append({'placement':p,'plane':plane,'selected_volume_count':int(selected.sum()),
                               **placement_geometry_metrics(cfgp,plane,overlay=True)})
    write_csv(output,'placement_metrics.csv',placements)
    effects=[]
    for w,h in [(2,15),(3,10),(5,6),(6,5)]:
        for z in [1,2,4,16,64]:
            for start in [1,2,10,31,1001]:
                c=GridConfig(w,h,z,start=start)
                d=projection(c,overlay=True)
                m=overlay_metrics(c,random_trials=12)
                effects.append({'X':w,'Y':h,'Z':z,'Start':start,
                    'volume_prime_density':float(d['selected_3d'].mean()),
                    **{k:m[k] for k in KEYS},'structural_score':m['structural_score'],
                    'coprime_residual_l2':m['coprime_residual_l2']})
    write_csv(output,'start_z_m30.csv',effects)
    print('Density, aspect ratio, symmetries, placements and Start/Z complete',flush=True)
    metadata={'configuration':config_dict(),'null_grid':asdict(cfg),'seed':seed,
        'trials':trials,'replicates':replicates,'null_alive_count':alive_count,
        'null_coprime_cell_count':len(allowed),'python':platform.python_version(),
        'numpy':np.__version__,'platform':platform.system(),'backend':'CPU / NumPy',
        'tail_definition':'inclusive one-sided empirical fractions, not formal p-values; ties isclose rtol=atol=1e-12',
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.glob('*.py'))}}
    (output/'manifest.json').write_text(json.dumps(metadata,indent=2,sort_keys=True)+'\n')
    clear_volume_cache();reset_config()


def make_plots(output):
    """Optional publication artifact; Matplotlib is already a GUI dependency."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with (output/'null_trials.csv').open() as f: rows=list(csv.DictReader(f))
    with (output/'null_controls.csv').open() as f: observed=next(csv.DictReader(f))
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    for ax,key in zip(axes,['beauty_score','fft_axis_ratio','fft_lowfreq_ratio']):
        for model,label,color in [('uniform_resampled','Uniform, resampled hits','#657a91'),('coprime_conditioned_resampled','Coprime-conditioned, resampled hits','#07806b')]:
            values=[float(r[key]) for r in rows if r['model']==model]
            ax.hist(values,bins=25,alpha=.55,label=label,color=color)
        ax.axvline(float(observed[key]),color='#b52222',linewidth=2,label='Observed primes')
        ax.set(title=key,xlabel='Metric value',ylabel='Trial count')
    axes[0].legend(fontsize=7)
    fig.suptitle('Exploratory null comparison: Linear 30×30×2, Start=1001 (XY full overlay)')
    fig.tight_layout()
    fig.savefig(output/'null_comparison.png',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results'/'scientific_audit')
    parser.add_argument('--trials',type=int,default=500)
    parser.add_argument('--replicates',type=int,default=50)
    parser.add_argument('--plots',action='store_true',help='Also render a null comparison PNG with Matplotlib')
    parser.add_argument('--seed',type=int,default=20260910)
    args=parser.parse_args()
    if args.trials<2 or args.replicates<1: parser.error('trials >= 2 and replicates >= 1 required')
    run(args.output,args.trials,args.seed,args.replicates)
    if args.plots: make_plots(args.output)
