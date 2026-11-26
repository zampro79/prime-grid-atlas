"""Recalculate demonstrations using the unchanged source; verify native sidecars.
python scripts/verify_examples.py --source ../clean-source --package ../separate-example-copy
Writes numerical-validation.json only; never rewrites application artifacts.
"""
import argparse
from pathlib import Path
import sys,json,hashlib,math,csv,subprocess
from datetime import datetime

S='eaf6c433722521c5f0dd6a6b07e112e643b5d05b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--source',type=Path,required=True);a.add_argument('--package',type=Path,required=True);v=a.parse_args()
    root=v.source.resolve();p=v.package.resolve();sys.path.insert(0,str(root))
    import numpy as np
    from app_config import AppConfig,set_config
    from compute_backend import configure_backend
    from atlas_engine import GridConfig,projection,overlay_metrics,placement_geometry_metrics,clear_volume_cache
    set_config(AppConfig(**load(p/'shared-profile.json')));configure_backend('CPU')
    assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==S
    assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain'])
    source=load(p/'source-origin.json')
    for name,h in source['all_tracked_python_sha256'].items():assert sha(root/name)==h
    nchecked=0
    def compare(actual,expected):
        nonlocal nchecked
        if isinstance(expected,dict):
            for k,val in expected.items():compare(actual[k],val)
        elif isinstance(expected,(int,float)):
            np.testing.assert_allclose(float(actual),expected,rtol=1e-12,atol=1e-12,equal_nan=False);nchecked+=1
        else:assert actual==expected,(actual,expected)
    # Independent integer oracle: trial division, not the application's sieve.
    def prime(n):return n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))
    integers=np.arange(1,63901).reshape(30,30,71)
    selected=np.fromiter((prime(int(n)) for n in integers.flat),bool,count=integers.size).reshape(integers.shape)
    hits=selected.sum(axis=0)
    np.testing.assert_array_equal(np.loadtxt(p/'01-prime-occupancy/hits.csv',delimiter=','),hits)
    prime_result=load(p/'01-prime-occupancy/results.json')
    compare(prime_result['counts'],{'selected_volume_cells':int(selected.sum()),'projected_occupied_cells':int(np.count_nonzero(hits)),'projected_total_cells':2130})
    compare(prime_result['metrics'],overlay_metrics(GridConfig(71,30,30,'Primes',2,'Linear',1,7),'XY',29,12))
    coprime=np.fromiter((math.gcd(int(n),2130)==1 for n in integers.flat),bool,count=integers.size).reshape(integers.shape)
    chits=coprime.sum(axis=0)
    np.testing.assert_array_equal(np.loadtxt(p/'02-coprime-support/hits.csv',delimiter=','),chits)
    compare(load(p/'02-coprime-support/results.json'),{'selected_volume_cells':int(coprime.sum()),'projected_occupied_cells':int(np.count_nonzero(chits)),'projected_total_cells':2130,'modulus':2130})
    # Direct NumPy definition, separately from engine fft_spectrum.
    work=(hits>0).astype(float);work-=work.mean()
    power=np.abs(np.fft.fftshift(np.fft.fft2(work)))**2;power[15,35]=0
    saved=np.loadtxt(p/'04-fft/log-power.csv',delimiter=',')
    expected=np.log1p(power);np.testing.assert_allclose(saved,expected,rtol=1e-12,atol=1e-12)
    total=power.sum();axis=np.zeros_like(power,bool);axis[15,:]=True;axis[:,35]=True;axis[15,35]=False
    yy,xx=np.indices(power.shape);radius=np.hypot(xx-35,yy-15);low=(radius>0)&(radius<=max(1,.18*radius.max()))
    probs=power.ravel()/total;probs=probs[probs>0]
    fm={'fft_peak_ratio':float(power.max()/total),'fft_axis_ratio':float(power[axis].sum()/total),
        'fft_lowfreq_ratio':float(power[low].sum()/total),'fft_spectral_entropy':float(-(probs*np.log2(probs)).sum()/math.log2(power.size-1))}
    compare(load(p/'04-fft/results.json'),fm)
    z,y,x=np.nonzero(selected);positions=np.column_stack((x,y,z))
    np.testing.assert_array_equal(np.loadtxt(p/'03-cartesian-3d/rendered-positions.csv',delimiter=',',skiprows=1),positions)
    r3=load(p/'03-cartesian-3d/results.json');assert r3['rendered_points']==r3['selected_points']==len(positions)==6406 and r3['subsampling'] is False
    # Same-implementation numerical repeatability checks, not independent proofs.
    rows=load(p/'05-placement-comparison/results.json');assert len(rows)==14
    new=[]
    for row in rows:
        clear_volume_cache();cfg=GridConfig(30,30,2,'Primes',2130,row['placement'],1001,7)
        new.append({'placement':row['placement'],'classification':row['classification'],**placement_geometry_metrics(cfg,'XY',1,True)})
    ref=next(r for r in new if r['placement']=='Linear')
    keys=('alive_density','local_entropy_mean','edge_density','global_entropy','fft_peak_ratio','fft_axis_ratio','fft_lowfreq_ratio','fft_spectral_entropy')
    for actual,expectedrow in zip(rows,new):
        expectedrow['distance_from_linear']=math.sqrt(sum((expectedrow[k]-ref[k])**2 for k in keys));compare(actual,expectedrow)
    scans=load(p/'06-parametric-scan/results.json');assert len(scans)==49 and len({(r['X'],r['Y']) for r in scans})==49
    assert {(r['X'],r['Y']) for r in scans}=={(x,y) for x in range(26,33) for y in range(26,33)}
    for row in scans:
        clear_volume_cache();compare(row,{'X':row['X'],'Y':row['Y'],'Z':2,**overlay_metrics(GridConfig(row['X'],row['Y'],2,'Primes',2,'Linear',1001,7),'XY',random_trials=12)})
    csv_counts={}
    for rel,original,idkey in [('05-placement-comparison/placements.csv',rows,'placement'),('06-parametric-scan/scan.csv',scans,'X')]:
        with (p/rel).open(newline='') as f:csvrows=list(csv.DictReader(f,delimiter=';'))
        assert len(csvrows)==len(original)
        lookup={(r['X'],r['Y']):r for r in original} if idkey=='X' else {r['placement']:r for r in original}
        for r in csvrows:
            other=lookup[(int(r['X']),int(r['Y']))] if idkey=='X' else lookup[r['placement']]
            for k,value in r.items():
                if isinstance(other[k],(int,float)):compare(float(value),other[k])
                else:assert value==str(other[k])
        csv_counts[rel]=len(csvrows)
    native=[]
    for f in sorted(p.rglob('*.manifest.json')):
        m=load(f);assert m['schema']=='pga.provenance/1.0' and m['application']['version']=='1.1.0'
        assert m['source']['git']=={'available':True,'commit':S,'dirty':False}
        assert m['source']['changed_since_initial_observation'] is False
        assert m['experiment']['status']=='completed'
        for k in ('experiment_started_at','experiment_completed_at','exported_at'):datetime.fromisoformat(m['experiment'][k].replace('Z','+00:00'))
        for s in m['source']['files']:assert sha(root/s['path'])==s['sha256']
        for o in m['outputs']:
            q=f.parent/o['path'];assert q.stat().st_size==o['size'] and sha(q)==o['sha256'] and o['status']=='complete'
        native.append({'path':str(f.relative_to(p)),'sha256':sha(f),'outputs':len(m['outputs']),'compute':m['compute'],'source_clean':True})
    assert len(native)==5
    for d in sorted(p.glob('*/editorial-metadata.json')):
        m=load(d);assert m['application_version']=='1.1.0' and m['source_commit']==S
    assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain'])
    report={'status':'PASS','source_commit':S,'application_version':'1.1.0','relative_tolerance':1e-12,'absolute_tolerance':1e-12,
        'independent_trial_division':{'prime_cells':int(selected.sum()),'projected_prime_support':int(np.count_nonzero(hits))},
        'independent_gcd':{'selected_cells':int(coprime.sum()),'projected_support':int(np.count_nonzero(chits))},
        'independent_numpy_fft':{'shape':list(saved.shape),'maximum_absolute_matrix_difference':float(np.max(np.abs(saved-expected))),'metrics':fm},
        '3d_positions_exactly_verified':len(positions),'3d_subsampling':False,
        'same_implementation_recalculations':{'comparison_rows':14,'scan_rows':49,'numeric_assertions':nchecked},
        'native_csv_rows':csv_counts,'native_sidecars':native,
        'limits':['Scan/comparison metric reruns use the same implementation; no new mathematical proof or significance claim.',
                  'Native producer backend unknown remains unknown; editorial CPU observation is recorded separately.']}
    (p/'numerical-validation.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('NUMERICAL AND NATIVE PROVENANCE VALIDATION PASS',nchecked)
if __name__=='__main__':main()
