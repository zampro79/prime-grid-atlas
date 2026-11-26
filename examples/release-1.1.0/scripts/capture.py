"""Real Prime Grid Atlas 1.1.0 capture; no simulated data or renderer.
Run from a real desktop with an existing compatible environment:
python scripts/capture.py --source ../clean-source --output ../new-capture
Outputs and this script must remain outside the clean source checkout.
Only save-dialog destinations and success notifications are automated.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from unittest.mock import patch

SOURCE_COMMIT = 'eaf6c433722521c5f0dd6a6b07e112e643b5d05b'
CASES = ['01-prime-occupancy', '02-coprime-support', '03-cartesian-3d',
         '04-fft', '05-placement-comparison', '06-parametric-scan', '07-provenance-export']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, obj):
    p.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.source.resolve(), args.output.resolve()
    assert not out.is_relative_to(root)
    def git(*a):
        return subprocess.check_output(['git', '-C', str(root), *a], text=True).strip()
    assert git('rev-parse', 'HEAD') == SOURCE_COMMIT
    assert not git('status', '--porcelain')
    out.mkdir(parents=True, exist_ok=False)
    for c in CASES:
        (out/c).mkdir()
    sys.path.insert(0, str(root))
    import numpy as np
    import qt_app
    from app_config import AppConfig, config_dict, set_config
    from atlas_engine import fft_spectrum, overlay_metrics
    from compute_backend import configure_backend, backend_state, should_use_gpu
    from provenance import collect_source_identity, utc_now
    from PySide6.QtWidgets import QApplication, QSplitter, QMessageBox
    from PySide6.QtGui import QFont
    from PySide6.QtCore import qVersion
    from OpenGL import GL
    assert qt_app.APP_VERSION == '1.1.0'
    set_config(AppConfig(baseline_seed=20261126, baseline_trials=12))
    configure_backend('CPU')
    app = QApplication([])
    assert app.platformName() not in ('offscreen', 'minimal')
    app.setStyle('Fusion')
    app.setFont(QFont('DejaVu Sans', 11))
    source = collect_source_identity(root, qt_app.PROVENANCE_SOURCE_FILES)
    assert source['git']['dirty'] is False
    write(out/'source-origin.json', {'metadata_kind':'editorial observation, not a native manifest',
        'source_commit':SOURCE_COMMIT, 'runtime_application_version':'1.1.0',
        'git_clean':True, 'source_identity':source,
        'all_tracked_python_sha256':{f:digest(root/f) for f in git('ls-files', '*.py').splitlines()}})
    write(out/'shared-profile.json', config_dict())
    environment = {'python':platform.python_version(), 'environment_kind':'existing author-provided virtual environment',
        'packages':{n:importlib.metadata.version(n) for n in ('numpy','PySide6','shiboken6','matplotlib','pyqtgraph','PyOpenGL')},
        'Qt':qVersion(), 'OS':platform.system(), 'architecture':platform.machine(),
        'qt_platform':app.platformName(), 'session_type':os.environ.get('XDG_SESSION_TYPE','not observed'),
        'style':'Fusion', 'font':'DejaVu Sans 11', 'requested_logical_size':[1900,1120]}
    write(out/'environment-public.json', environment)
    window = qt_app.MainWindow()
    window.backend.setCurrentText('CPU')
    window.resize(1900,1120)
    window.show()
    window.findChild(QSplitter).setSizes([650,1250])
    records=[]
    def settle(seconds=.3):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            app.processEvents()
            time.sleep(.005)
        window.timer.stop()
    def config():
        return qt_app._grid_configuration(window.config(), window.plane.currentText(),
            window.level.value(), window.overlay.isChecked(), window.view_mode.currentText())
    def capture(widget, case, filename, kind='desktop Qt widget screenshot'):
        settle()
        pix=widget.grab()
        assert not pix.isNull() and pix.save(str(out/case/filename),'PNG')
        rec={'path':case+'/'+filename,'size':[pix.width(),pix.height()], 'kind':kind,
             'captured_at':utc_now(),'qt_platform':app.platformName(),
             'device_pixel_ratio':widget.devicePixelRatioF()}
        records.append(rec)
        return rec
    def private_text(obj):
        text=json.dumps(obj)
        return any(v in text for v in ('/home/','/Users/','/tmp/','file://', 'environment_prefix','sys.executable'))
    def export(method, case, filename):
        with patch.object(qt_app.QFileDialog, 'getSaveFileName',return_value=(str(out/case/filename),'')), \
             patch.object(qt_app.QMessageBox,'information'):
            method()
        target=out/case/filename
        assert target.is_file()
        native=target.with_name(target.name+'.manifest.json')
        m=json.loads(native.read_text())
        assert not private_text(m), 'Native manifest contains private data; stop public preparation'
        assert m['application']['version']=='1.1.0' and m['source']['git']['commit']==SOURCE_COMMIT
        assert m['source']['git']['dirty'] is False and m['experiment']['status']=='completed'
        return m
    def metadata(case, configuration, **extra):
        assert not should_use_gpu(10**9)
        write(out/case/'configuration.json', configuration)
        write(out/case/'editorial-metadata.json', {'metadata_kind':'editorial observation, not native provenance',
            'source_commit':SOURCE_COMMIT, 'application_version':'1.1.0', 'source_git_clean':True,
            'observed_at':utc_now(), 'profile':'../shared-profile.json','source_identity':'../source-origin.json',
            'environment':'../environment-public.json', 'configuration':'configuration.json',
            'compute':{'requested':'CPU','observed_policy':backend_state(),
                       'gpu_path_for_large_input':should_use_gpu(10**9),
                       'evidence':'CPU explicitly selected; real NumPy arrays returned; unchanged CPU branch exercised'},
            'randomness':{'baseline_seed':20261126,'baseline_trials':12,'generator':'numpy.random.default_rng',
                          'independent_seed_for_deterministic_projection_fft_3d':None}, **extra})
    def error_dialog(*a,**k):
        raise RuntimeError('Application dialog: '+str(a[-1]))
    try:
        with patch.object(QMessageBox,'critical',side_effect=error_dialog), \
             patch.object(QMessageBox,'warning',side_effect=error_dialog):
            c=CASES[0]
            window.set_dims(71,30,30);window.start_spin.setValue(1)
            window.set_mode('Primes');window.param.setValue(2)
            window.placement.setCurrentText('Linear');window.placement_param.setValue(7)
            window.plane.setCurrentText('XY');window.level.setValue(29)
            window.overlay.setChecked(True);window.show_numbers.setChecked(False)
            window.view_mode.setCurrentText('Classic');settle();window.render();settle()
            assert window.current_data is not None
            window.findChild(QSplitter).setSizes([650,1250]);settle()
            window.image_view.reset_zoom()
            data=window.current_data
            metrics=overlay_metrics(window.config(),'XY',29,random_trials=12)
            counts={'selected_volume_cells':int(data['selected_3d'].sum()),
                    'projected_occupied_cells':int(np.count_nonzero(data['hits'])),
                    'projected_total_cells':int(data['hits'].size)}
            write(out/c/'results.json',{'counts':counts,'metrics':metrics})
            np.savetxt(out/c/'hits.csv',data['hits'],delimiter=',',fmt='%d')
            capture(window,c,'interface.png')
            export(window.save_png,c,'viewport.png')
            records.append({'path':c+'/viewport.png','kind':'native desktop viewport PNG export',
                            'captured_at':utc_now()})
            metadata(c,config(),display={'numbers':False,'grid':True,'zoom':'native fitInView'})
            print('EX-01 complete',counts,flush=True)

            c=CASES[3]
            spectrum,fft_metrics=fft_spectrum(data,True)
            np.savetxt(out/c/'log-power.csv',spectrum,delimiter=',',fmt='%.17g')
            write(out/c/'results.json',fft_metrics)
            window.show_matrix_tab(spectrum,'FFT | binary prime occupancy | 71 x 30 x 30 | Start=1 | XY | DC removed')
            settle();window.analysis_view.reset_zoom()
            capture(window,c,'interface.png')
            capture(window.analysis_view,c,'viewport.png','desktop Qt FFT viewport capture')
            export(window.save_fft,c,'native-fft.png')
            metadata(c,config(),display={'matrix_origin':'lower (vertical flip in Qt)',
                'normalization':'mean-centered binary hits > 0; fftshift power; DC=0; log1p(power)',
                'qualitative_capture':'Application viewport has no quantitative frequency axes or colorbar',
                'native_matplotlib_export':'native-fft.png; index axes and colorbar; unchanged application'})
            print('EX-04 FFT complete',flush=True)

            c=CASES[2]
            window.selected_only_3d.setChecked(True);window.geometry_3d.setCurrentText('Cartesian grid')
            window.show_3d();settle(1)
            assert window.gl_view.context() and window.gl_view.context().isValid()
            # Native camera control, without changing selected points.
            window._zoom_3d(.9);settle(.5)
            window.gl_view.makeCurrent()
            renderer={k:GL.glGetString(v).decode() for k,v in [('vendor',GL.GL_VENDOR),('renderer',GL.GL_RENDERER),('version',GL.GL_VERSION)]}
            window.gl_view.doneCurrent()
            positions=np.asarray(window.gl_items[0].pos)
            assert len(positions)==min(counts['selected_volume_cells'],config_dict()['max_3d_points'])
            capture(window,c,'interface.png')
            framebuffer=window.gl_view.grabFramebuffer()
            assert not framebuffer.isNull() and framebuffer.save(str(out/c/'framebuffer.png'),'PNG')
            records.append({'path':c+'/framebuffer.png','size':[framebuffer.width(),framebuffer.height()],
                            'kind':'native desktop OpenGL framebuffer','captured_at':utc_now()})
            np.savetxt(out/c/'rendered-positions.csv',positions,delimiter=',',fmt='%.9g',header='x,y,z',comments='')
            write(out/c/'results.json',{'selected_points':counts['selected_volume_cells'],
                'rendered_points':len(positions),'subsampling':len(positions)<counts['selected_volume_cells'],
                'geometry':'Cartesian grid','context_valid':True,'renderer':renderer})
            metadata(c,config(),display={'selected_only':True,'point_size':5.0,'max_points':2000000,
                'camera':{'elevation':24,'azimuth':42,'distance':window._gl_distance,
                          'center':[35,14.5,14.5]},'renderer':renderer})
            environment['OpenGL']=renderer;environment['device_pixel_ratio']=window.devicePixelRatioF()
            write(out/'environment-public.json',environment)
            print('EX-03 OpenGL complete',renderer,flush=True)

            c=CASES[1]
            window.tabs.setCurrentIndex(0);window.set_mode('Coprimes with N');window.param.setValue(2130)
            settle();window.render();settle();window.findChild(QSplitter).setSizes([650,1250]);settle()
            window.image_view.reset_zoom()
            data=window.current_data
            summary={'selected_volume_cells':int(data['selected_3d'].sum()),
                'projected_occupied_cells':int(np.count_nonzero(data['hits'])),
                'projected_total_cells':int(data['hits'].size),'modulus':2130}
            write(out/c/'results.json',summary);np.savetxt(out/c/'hits.csv',data['hits'],delimiter=',',fmt='%d')
            capture(window,c,'interface.png');export(window.save_png,c,'viewport.png')
            records.append({'path':c+'/viewport.png','kind':'native desktop viewport PNG export','captured_at':utc_now()})
            metadata(c,config(),display={'zoom':'native fitInView'})
            print('EX-02 complete',summary,flush=True)

            c=CASES[4]
            window.set_dims(30,30,2);window.start_spin.setValue(1001);window.set_mode('Primes');window.level.setValue(1)
            settle();window.render();window.open_placement_comparison()
            comparison=window.comparison_tab;comparison.start_comparison()
            deadline=time.monotonic()+180
            while comparison.running and time.monotonic()<deadline:app.processEvents()
            assert not comparison.running and len(comparison.rows)==14 and comparison._experiment_status=='completed'
            comparison.table.resizeColumnsToContents()
            capture(window,c,'interface.png');export(comparison.export_csv,c,'placements.csv')
            write(out/c/'results.json',comparison.rows)
            metadata(c,json.loads((out/c/'placements.config.json').read_text()),
                placement_randomness={'parameter':7,'derived_seed':(30*73856093 ^ 30*19349663 ^ 7*2654435761)&0xffffffff,
                    'derivation':'(X*73856093 XOR Y*19349663 XOR placement_parameter*2654435761) AND 0xFFFFFFFF'},
                display={'table':'Full 14 rows; wide-column excerpt, full CSV authoritative'})
            print('EX-05 complete',flush=True)

            c=CASES[5]
            window.open_scan();scan=window.scan_tab;scan.backend.setCurrentText('CPU')
            scan.x1.setValue(26);scan.x2.setValue(32);scan.y1.setValue(26);scan.y2.setValue(32)
            scan.z.setValue(2);scan.trials.setValue(12);scan.start_scan()
            deadline=time.monotonic()+180
            while scan.thread is not None and time.monotonic()<deadline:app.processEvents();time.sleep(.002)
            assert scan.thread is None and scan.worker is None and len(scan.rows)==49
            assert scan._experiment_status=='completed'
            scan.table.resizeColumnsToContents();capture(window,c,'interface.png')
            native=export(scan.export_csv,c,'scan.csv');write(out/c/'results.json',scan.rows)
            metadata(c,scan.scan_metadata,display={'table':'49 computed rows; visible row/column excerpt; full CSV authoritative'},
                     worker_cleanup={'thread':None,'worker':None,'status':'finished through native signals'})
            metadata(CASES[6],scan.scan_metadata,native_manifest='../06-parametric-scan/scan.csv.manifest.json',
                     native_output='../06-parametric-scan/scan.csv',
                     note='Reuse EX-06 unchanged native files, not duplicated; no provenance inspector UI exists')
            write(out/CASES[6]/'native-manifest-explanation.json',{'metadata_kind':'explanation, not a native manifest',
                'native_manifest':'../06-parametric-scan/scan.csv.manifest.json',
                'native_manifest_sha256':digest(out/c/'scan.csv.manifest.json'),
                'application':native['application'],'experiment':native['experiment'],'compute':native['compute'],
                'outputs':native['outputs']})
            print('EX-06 and EX-07 complete',flush=True)
            write(out/'capture-records.json',records)
    finally:
        window.close();settle(.3);app.quit()
    assert not git('status','--porcelain')
    write(out/'desktop-validation.json',{'application_version':'1.1.0','source_commit':SOURCE_COMMIT,
        'source_git_clean_before_and_after':True, 'stages_completed':['2D prime','FFT real Matplotlib native export',
        'OpenGL context and framebuffer','coprime 2D','14 placement rows','49 scan rows','native exports',
        'scan worker and thread normal completion','window.close and app.quit'],
        'finished_at':utc_now(),'R08-08':'HIGH / OPEN / NOT REPRODUCED / ROOT CAUSE UNKNOWN',
        'scope':'One successful capture process on the observed Linux Wayland desktop; no general stability guarantee'})
    print('CAPTURE COMPLETE',flush=True)

if __name__=='__main__':
    main()
