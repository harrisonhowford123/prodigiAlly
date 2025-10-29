-------------------------------------
Translated Report (Full Report Below)
-------------------------------------

Process:               Python [3557]
Path:                  /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents/MacOS/Python
Identifier:            org.python.python
Version:               3.13.6 (3.13.6)
Code Type:             X86-64 (Native)
Parent Process:        Python [3398]
Responsible:           Python [3398]
User ID:               502

Date/Time:             2025-10-29 16:48:04.9644 +0000
OS Version:            macOS 12.7.6 (21H1320)
Report Version:        12
Anonymous UUID:        90C62505-A070-17C7-0B98-6C16CEF1F677

Sleep/Wake UUID:       2459E341-1A8C-4234-858A-430599A5FE1B

Time Awake Since Boot: 17000 seconds
Time Since Wake:       814 seconds

System Integrity Protection: enabled

Crashed Thread:        13

Exception Type:        EXC_CRASH (SIGABRT)
Exception Codes:       0x0000000000000000, 0x0000000000000000
Exception Note:        EXC_CORPSE_NOTIFY

Application Specific Information:
abort() called


Application Specific Backtrace 0:
0   CoreFoundation                      0x00007ff812ea96e3 __exceptionPreprocess + 242
1   libobjc.A.dylib                     0x00007ff812c098bb objc_exception_throw + 48
2   CoreFoundation                      0x00007ff812ed1fc6 -[NSException raise] + 9
3   AppKit                              0x00007ff815892c44 -[NSWindow(NSWindow_Theme) _postWindowNeedsToResetDragMarginsUnlessPostingDisabled] + 321
4   AppKit                              0x00007ff81587ebf4 -[NSWindow _initContent:styleMask:backing:defer:contentView:] + 1288
5   AppKit                              0x00007ff81587e6e6 -[NSWindow initWithContentRect:styleMask:backing:defer:] + 42
6   AppKit                              0x00007ff815b5f627 -[NSWindow initWithContentRect:styleMask:backing:defer:screen:] + 50
7   libqcocoa.dylib                     0x000000011186057f _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 247359
8   libqcocoa.dylib                     0x0000000111835074 _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 69940
9   libqcocoa.dylib                     0x000000011182c3eb _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 33963
10  libqcocoa.dylib                     0x000000011182bce8 _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 32168
11  QtGui                               0x000000010f59a5b7 _ZN14QWindowPrivate6createEb + 471
12  QtWidgets                           0x000000010eead285 _ZN14QWidgetPrivate6createEv + 1109
13  QtWidgets                           0x000000010eeaa46e _ZN7QWidget6createEybb + 382
14  QtWidgets                           0x000000010eec19a9 _ZN14QWidgetPrivate10setVisibleEb + 825
15  QtWidgets                           0x000000010f0db4c2 _ZN14QDialogPrivate10setVisibleEb + 450
16  QtWidgets.abi3.so                   0x000000010e9a68ae _ZN10sipQDialog10setVisibleEb + 110
17  QtWidgets.abi3.so                   0x000000010eaa09e4 _ZL17meth_QDialog_openP7_objectS0_ + 148
18  Python                              0x000000010b7b79fe cfunction_call + 110
19  Python                              0x000000010b8f7067 _PyEval_EvalFrameDefault + 86743
20  Python                              0x000000010b732004 method_vectorcall + 468
21  Python                              0x000000010ba4b8e2 thread_run + 146
22  Python                              0x000000010b9bb864 pythread_wrapper + 36
23  libsystem_pthread.dylib             0x00007ff812d674e1 _pthread_start + 125
24  libsystem_pthread.dylib             0x00007ff812d62f6b thread_start + 15


Thread 0::  Dispatch queue: com.apple.main-thread
0   libsystem_kernel.dylib        	    0x7ff812d2d3aa __psynch_cvwait + 10
1   libsystem_pthread.dylib       	    0x7ff812d67a6f _pthread_cond_wait + 1249
2   Python                        	       0x10b95c812 take_gil + 466
3   Python                        	       0x10b9a130d _PyThreadState_Attach + 45
4   Python                        	       0x10b9a2900 PyGILState_Ensure + 48
5   sip.cpython-313-darwin.so     	       0x10b2f0391 sip_api_is_py_method_12_8 + 65
6   QtCore.abi3.so                	       0x1103ee21c sipQObject::eventFilter(QObject*, QEvent*) + 60
7   QtCore                        	       0x10fe0a004 QCoreApplicationPrivate::sendThroughObjectEventFilters(QObject*, QEvent*) + 244
8   QtWidgets                     	       0x10ee6bb20 QApplicationPrivate::notify_helper(QObject*, QEvent*) + 288
9   QtWidgets                     	       0x10ee6caf6 QApplication::notify(QObject*, QEvent*) + 502
10  QtWidgets.abi3.so             	       0x10e9b84e5 sipQApplication::notify(QObject*, QEvent*) + 229
11  QtCore                        	       0x10fe0a8a3 QCoreApplication::sendSpontaneousEvent(QObject*, QEvent*) + 147
12  QtWidgets                     	       0x10eeb1203 QWidgetPrivate::drawWidget(QPaintDevice*, QRegion const&, QPoint const&, QFlags<QWidgetPrivate::DrawWidgetFlag>, QPainter*, QWidgetRepaintManager*) + 3987
13  QtWidgets                     	       0x10eed6b1e QWidgetRepaintManager::paintAndFlush() + 5806
14  QtWidgets                     	       0x10eed6e1c QWidgetRepaintManager::sync() + 268
15  QtWidgets                     	       0x10eec2810 QWidget::event(QEvent*) + 1632
16  QtWidgets.abi3.so             	       0x10e9cd4ef sipQWidget::event(QEvent*) + 191
17  QtWidgets                     	       0x10ee6bb34 QApplicationPrivate::notify_helper(QObject*, QEvent*) + 308
18  QtWidgets                     	       0x10ee6caf6 QApplication::notify(QObject*, QEvent*) + 502
19  QtWidgets.abi3.so             	       0x10e9b84e5 sipQApplication::notify(QObject*, QEvent*) + 229
20  QtCore                        	       0x10fe0a7a3 QCoreApplication::sendEvent(QObject*, QEvent*) + 147
21  QtCore                        	       0x10fe0af8e QCoreApplicationPrivate::sendPostedEvents(QObject*, int, QThreadData*) + 542
22  libqcocoa.dylib               	       0x11180352a 0x1117eb000 + 99626
23  libqcocoa.dylib               	       0x11180484a 0x1117eb000 + 104522
24  CoreFoundation                	    0x7ff812e2e0ab __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__ + 17
25  CoreFoundation                	    0x7ff812e2e013 __CFRunLoopDoSource0 + 180
26  CoreFoundation                	    0x7ff812e2dd8d __CFRunLoopDoSources0 + 242
27  CoreFoundation                	    0x7ff812e2c7a8 __CFRunLoopRun + 892
28  CoreFoundation                	    0x7ff812e2bd6c CFRunLoopRunSpecific + 562
29  HIToolbox                     	    0x7ff81bade5e6 RunCurrentEventLoopInMode + 292
30  HIToolbox                     	    0x7ff81bade34a ReceiveNextEventCommon + 594
31  HIToolbox                     	    0x7ff81bade0e5 _BlockUntilNextEventMatchingListInModeWithFilter + 70
32  AppKit                        	    0x7ff81586aaa9 _DPSNextEvent + 927
33  AppKit                        	    0x7ff815869166 -[NSApplication(NSEvent) _nextEventMatchingEventMask:untilDate:inMode:dequeue:] + 1394
34  AppKit                        	    0x7ff81585b818 -[NSApplication run] + 586
35  libqcocoa.dylib               	       0x111802069 0x1117eb000 + 94313
36  QtCore                        	       0x10fe13c86 QEventLoop::exec(QFlags<QEventLoop::ProcessEventsFlag>) + 534
37  QtCore                        	       0x10fe0a4eb QCoreApplication::exec() + 203
38  QtWidgets.abi3.so             	       0x10eaa904c meth_QApplication_exec(_object*, _object*) + 92
39  Python                        	       0x10b7b79fe cfunction_call + 110
40  Python                        	       0x10b8ee652 _PyEval_EvalFrameDefault + 51394
41  Python                        	       0x10b8dfd9f PyEval_EvalCode + 143
42  Python                        	       0x10b8d9851 builtin_exec + 449
43  Python                        	       0x10b8f1c80 _PyEval_EvalFrameDefault + 65264
44  Python                        	       0x10b731f09 method_vectorcall + 217
45  Python                        	       0x10b8f2166 _PyEval_EvalFrameDefault + 66518
46  Python                        	       0x10b8dfd9f PyEval_EvalCode + 143
47  Python                        	       0x10b9a4348 run_eval_code_obj + 136
48  Python                        	       0x10b9a3d2a run_mod + 154
49  Python                        	       0x10b9a6142 _PyRun_SimpleStringFlagsWithName + 274
50  Python                        	       0x10b9cfc47 Py_RunMain + 1031
51  Python                        	       0x10b9d141a pymain_main + 378
52  Python                        	       0x10b9d152b Py_BytesMain + 43
53  dyld                          	       0x11331d52e start + 462

Thread 1:
0   libsystem_kernel.dylib        	    0x7ff812d32d1a __select + 10
1   select.cpython-313-darwin.so  	       0x10af4ae32 select_select_impl + 450
2   Python                        	       0x10b8f197e _PyEval_EvalFrameDefault + 64494
3   Python                        	       0x10b805c34 slot_tp_init + 340
4   Python                        	       0x10b7f70f7 type_call + 135
5   Python                        	       0x10b8ee652 _PyEval_EvalFrameDefault + 51394
6   Python                        	       0x10b732004 method_vectorcall + 468
7   Python                        	       0x10ba4b8e2 thread_run + 146
8   Python                        	       0x10b9bb864 pythread_wrapper + 36
9   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
10  libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 2:
0   libsystem_kernel.dylib        	    0x7ff812d32d1a __select + 10
1   Tcl                           	       0x10b4fb467 0x10b30e000 + 2020455
2   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
3   libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 3:: Thread (pooled)
0   libsystem_kernel.dylib        	    0x7ff812d2d3aa __psynch_cvwait + 10
1   libsystem_pthread.dylib       	    0x7ff812d67a6f _pthread_cond_wait + 1249
2   QtCore                        	       0x10ffc440a 0x10fd70000 + 2442250
3   QtCore                        	       0x10ffc42a4 QWaitCondition::wait(QMutex*, QDeadlineTimer) + 84
4   QtCore                        	       0x10ffbe9cb 0x10fd70000 + 2419147
5   QtCore                        	       0x10ffb60ef 0x10fd70000 + 2384111
6   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
7   libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 4:: Thread (pooled)
0   libsystem_kernel.dylib        	    0x7ff812d2d3aa __psynch_cvwait + 10
1   libsystem_pthread.dylib       	    0x7ff812d67a6f _pthread_cond_wait + 1249
2   QtCore                        	       0x10ffc440a 0x10fd70000 + 2442250
3   QtCore                        	       0x10ffc42a4 QWaitCondition::wait(QMutex*, QDeadlineTimer) + 84
4   QtCore                        	       0x10ffbe9cb 0x10fd70000 + 2419147
5   QtCore                        	       0x10ffb60ef 0x10fd70000 + 2384111
6   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
7   libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 5:: Thread (pooled)
0   libsystem_kernel.dylib        	    0x7ff812d2d3aa __psynch_cvwait + 10
1   libsystem_pthread.dylib       	    0x7ff812d67a6f _pthread_cond_wait + 1249
2   QtCore                        	       0x10ffc440a 0x10fd70000 + 2442250
3   QtCore                        	       0x10ffc42a4 QWaitCondition::wait(QMutex*, QDeadlineTimer) + 84
4   QtCore                        	       0x10ffbe9cb 0x10fd70000 + 2419147
5   QtCore                        	       0x10ffb60ef 0x10fd70000 + 2384111
6   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
7   libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 6:: Thread (pooled)
0   libsystem_kernel.dylib        	    0x7ff812d2d3aa __psynch_cvwait + 10
1   libsystem_pthread.dylib       	    0x7ff812d67a6f _pthread_cond_wait + 1249
2   QtCore                        	       0x10ffc440a 0x10fd70000 + 2442250
3   QtCore                        	       0x10ffc42a4 QWaitCondition::wait(QMutex*, QDeadlineTimer) + 84
4   QtCore                        	       0x10ffbe9cb 0x10fd70000 + 2419147
5   QtCore                        	       0x10ffb60ef 0x10fd70000 + 2384111
6   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
7   libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 7:
0   libsystem_pthread.dylib       	    0x7ff812d62f48 start_wqthread + 0

Thread 8:: com.apple.NSEventThread
0   libsystem_kernel.dylib        	    0x7ff812d2a93a mach_msg_trap + 10
1   libsystem_kernel.dylib        	    0x7ff812d2aca8 mach_msg + 56
2   CoreFoundation                	    0x7ff812e2e29d __CFRunLoopServiceMachPort + 319
3   CoreFoundation                	    0x7ff812e2c928 __CFRunLoopRun + 1276
4   CoreFoundation                	    0x7ff812e2bd6c CFRunLoopRunSpecific + 562
5   AppKit                        	    0x7ff8159d8572 _NSEventThread + 132
6   libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
7   libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15

Thread 9:
0   libsystem_pthread.dylib       	    0x7ff812d62f48 start_wqthread + 0

Thread 10:
0   libsystem_pthread.dylib       	    0x7ff812d62f48 start_wqthread + 0

Thread 11:
0   libsystem_pthread.dylib       	    0x7ff812d62f48 start_wqthread + 0

Thread 12:
0   libsystem_pthread.dylib       	    0x7ff812d62f48 start_wqthread + 0

Thread 13 Crashed:
0   libsystem_kernel.dylib        	    0x7ff812d30fce __pthread_kill + 10
1   libsystem_pthread.dylib       	    0x7ff812d671ff pthread_kill + 263
2   libsystem_c.dylib             	    0x7ff812cb2d14 abort + 123
3   libc++abi.dylib               	    0x7ff812d23082 abort_message + 241
4   libc++abi.dylib               	    0x7ff812d1425d demangling_terminate_handler() + 266
5   libobjc.A.dylib               	    0x7ff812c10e39 _objc_terminate() + 96
6   libc++abi.dylib               	    0x7ff812d224a7 std::__terminate(void (*)()) + 8
7   libc++abi.dylib               	    0x7ff812d24d05 __cxxabiv1::failed_throw(__cxxabiv1::__cxa_exception*) + 27
8   libc++abi.dylib               	    0x7ff812d24ccc __cxa_throw + 116
9   libobjc.A.dylib               	    0x7ff812c099b9 objc_exception_throw + 302
10  CoreFoundation                	    0x7ff812ed1fc6 -[NSException raise] + 9
11  AppKit                        	    0x7ff815892c44 -[NSWindow(NSWindow_Theme) _postWindowNeedsToResetDragMarginsUnlessPostingDisabled] + 321
12  AppKit                        	    0x7ff81587ebf4 -[NSWindow _initContent:styleMask:backing:defer:contentView:] + 1288
13  AppKit                        	    0x7ff81587e6e6 -[NSWindow initWithContentRect:styleMask:backing:defer:] + 42
14  AppKit                        	    0x7ff815b5f627 -[NSWindow initWithContentRect:styleMask:backing:defer:screen:] + 50
15  libqcocoa.dylib               	       0x11186057f 0x1117eb000 + 480639
16  libqcocoa.dylib               	       0x111835074 0x1117eb000 + 303220
17  libqcocoa.dylib               	       0x11182c3eb 0x1117eb000 + 267243
18  libqcocoa.dylib               	       0x11182bce8 0x1117eb000 + 265448
19  QtGui                         	       0x10f59a5b7 QWindowPrivate::create(bool) + 471
20  QtWidgets                     	       0x10eead285 QWidgetPrivate::create() + 1109
21  QtWidgets                     	       0x10eeaa46e QWidget::create(unsigned long long, bool, bool) + 382
22  QtWidgets                     	       0x10eec19a9 QWidgetPrivate::setVisible(bool) + 825
23  QtWidgets                     	       0x10f0db4c2 QDialogPrivate::setVisible(bool) + 450
24  QtWidgets.abi3.so             	       0x10e9a68ae sipQDialog::setVisible(bool) + 110
25  QtWidgets.abi3.so             	       0x10eaa09e4 meth_QDialog_open(_object*, _object*) + 148
26  Python                        	       0x10b7b79fe cfunction_call + 110
27  Python                        	       0x10b8f7067 _PyEval_EvalFrameDefault + 86743
28  Python                        	       0x10b732004 method_vectorcall + 468
29  Python                        	       0x10ba4b8e2 thread_run + 146
30  Python                        	       0x10b9bb864 pythread_wrapper + 36
31  libsystem_pthread.dylib       	    0x7ff812d674e1 _pthread_start + 125
32  libsystem_pthread.dylib       	    0x7ff812d62f6b thread_start + 15


Thread 13 crashed with X86 Thread State (64-bit):
  rax: 0x0000000000000000  rbx: 0x000070000b265000  rcx: 0x000070000b262b88  rdx: 0x0000000000000000
  rdi: 0x000000000000be13  rsi: 0x0000000000000006  rbp: 0x000070000b262bb0  rsp: 0x000070000b262b88
   r8: 0x000070000b262a50   r9: 0x00007ff812d25f9b  r10: 0x0000000000000000  r11: 0x0000000000000246
  r12: 0x000000000000be13  r13: 0x0000003000000008  r14: 0x0000000000000006  r15: 0x0000000000000016
  rip: 0x00007ff812d30fce  rfl: 0x0000000000000246  cr2: 0x0000000000000000
  
Logical CPU:     0
Error Code:      0x02000148 
Trap Number:     133


Binary Images:
    0x7ff812d29000 -     0x7ff812d60fff libsystem_kernel.dylib (*) <2fe67e94-4a5e-3506-9e02-502f7270f7ef> /usr/lib/system/libsystem_kernel.dylib
    0x7ff812d61000 -     0x7ff812d6cfff libsystem_pthread.dylib (*) <5a5f7316-85b7-315e-baf3-76211ee65604> /usr/lib/system/libsystem_pthread.dylib
       0x10b6a0000 -        0x10bb56fff org.python.python (3.13.6, (c) 2001-2024 Python Software Foundation.) <3e3e51d1-06ad-3908-8a89-b57769b0eb3d> /Library/Frameworks/Python.framework/Versions/3.13/Python
       0x10b2e7000 -        0x10b2fcfff sip.cpython-313-darwin.so (*) <3c3502c7-dcd4-34eb-b1ff-63106cb62a4e> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/sip.cpython-313-darwin.so
       0x110382000 -        0x110533fff QtCore.abi3.so (*) <48217fd0-a431-3edf-ac4c-834e19c03d50> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/QtCore.abi3.so
       0x10fd70000 -        0x1102a5fff QtCore (*) <5dd15e14-a793-339f-b921-6bb4cd992e77> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/Qt6/lib/QtCore.framework/Versions/A/QtCore
       0x10ee5e000 -        0x10f347fff QtWidgets (*) <bc196354-97c2-3137-9f3d-e44718bd0753> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/Qt6/lib/QtWidgets.framework/Versions/A/QtWidgets
       0x10e880000 -        0x10eb3dfff QtWidgets.abi3.so (*) <ae8322b3-396f-3aed-8d75-b1ba17c952ee> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/QtWidgets.abi3.so
       0x1117eb000 -        0x111895fff libqcocoa.dylib (*) <70a50108-a972-33e4-9472-85b1c247086f> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/Qt6/plugins/platforms/libqcocoa.dylib
    0x7ff812dae000 -     0x7ff8132b0fff com.apple.CoreFoundation (6.9) <fdd28505-5456-3c40-a5ba-7890b064db39> /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation
    0x7ff81bab0000 -     0x7ff81bda3fff com.apple.HIToolbox (2.1.1) <913d3d2e-4e4c-3907-98fe-8f4abd551297> /System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/HIToolbox
    0x7ff81582c000 -     0x7ff8166bbfff com.apple.AppKit (6.9) <5dd484cf-ed6a-3633-b42e-6518aeecd5b9> /System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
       0x113318000 -        0x113383fff dyld (*) <eea022bb-a6ab-3cd1-8ac1-54ce8cfd3333> /usr/lib/dyld
       0x10af48000 -        0x10af4cfff select.cpython-313-darwin.so (*) <4467f668-cf5f-3afb-9a37-f1c19b65e194> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/lib-dynload/select.cpython-313-darwin.so
       0x10b30e000 -        0x10b528fff com.tcltk.tcllibrary (8.6.16) <59d3fb5b-ac36-38c1-9d76-61d1c534290a> /Library/Frameworks/Python.framework/Versions/3.13/Frameworks/Tcl.framework/Versions/8.6/Tcl
    0x7ff812c31000 -     0x7ff812cb9fff libsystem_c.dylib (*) <202d7260-ea46-3956-a471-19c9bcf45274> /usr/lib/system/libsystem_c.dylib
    0x7ff812d13000 -     0x7ff812d28fff libc++abi.dylib (*) <69ac868b-1157-364a-984a-5ef26973f661> /usr/lib/libc++abi.dylib
    0x7ff812bf3000 -     0x7ff812c2dfff libobjc.A.dylib (*) <b36a2b52-68a9-3e44-b927-71c24be1272f> /usr/lib/libobjc.A.dylib
       0x10f4a8000 -        0x10fc28fff QtGui (*) <8c94e242-8015-33e9-83b8-9ea4af68851e> /Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/PyQt6/Qt6/lib/QtGui.framework/Versions/A/QtGui

External Modification Summary:
  Calls made by other processes targeting this process:
    task_for_pid: 0
    thread_create: 0
    thread_set_state: 0
  Calls made by this process:
    task_for_pid: 0
    thread_create: 0
    thread_set_state: 0
  Calls made by all processes on this machine:
    task_for_pid: 0
    thread_create: 0
    thread_set_state: 0

VM Region Summary:
ReadOnly portion of Libraries: Total=1.0G resident=0K(0%) swapped_out_or_unallocated=1.0G(100%)
Writable regions: Total=740.1M written=0K(0%) resident=0K(0%) swapped_out=0K(0%) unallocated=740.1M(100%)

                                VIRTUAL   REGION 
REGION TYPE                        SIZE    COUNT (non-coalesced) 
===========                     =======  ======= 
Accelerate framework               128K        1 
Activity Tracing                   256K        1 
CG backing stores                 1920K        4 
ColorSync                          224K       26 
CoreAnimation                       56K        6 
CoreGraphics                        12K        2 
CoreUI image data                  792K        5 
Foundation                          16K        1 
Kernel Alloc Once                    8K        1 
MALLOC                           282.6M      104 
MALLOC guard page                   32K        8 
MALLOC_LARGE (reserved)            384K        1         reserved VM address space (unallocated)
MALLOC_NANO (reserved)           384.0M        1         reserved VM address space (unallocated)
STACK GUARD                         56K       14 
Stack                             53.2M       15 
VM_ALLOCATE                       17.1M       38 
__CTF                               756        1 
__DATA                            26.1M      510 
__DATA_CONST                      23.6M      293 
__DATA_DIRTY                      1388K      169 
__FONT_DATA                          4K        1 
__LINKEDIT                       661.1M       87 
__OBJC_RO                         82.9M        1 
__OBJC_RW                         3200K        2 
__TEXT                           392.7M      518 
__UNICODE                          592K        1 
dyld private memory               1024K        1 
mapped file                      393.2M       54 
shared memory                      768K       15 
===========                     =======  ======= 
TOTAL                              2.3G     1881 
TOTAL, minus reserved VM space     1.9G     1881 



-----------
Full Report
-----------

{"app_name":"Python","timestamp":"2025-10-29 16:48:05.00 +0000","app_version":"3.13.6","slice_uuid":"bcb933e3-dab8-3b2a-a687-36b51de7637e","build_version":"3.13.6","platform":1,"bundleID":"org.python.python","share_with_app_devs":1,"is_first_party":0,"bug_type":"309","os_version":"macOS 12.7.6 (21H1320)","incident_id":"6341A167-F974-4E34-8C29-E296F75A13BB","name":"Python"}
{
  "uptime" : 17000,
  "procLaunch" : "2025-10-29 16:47:33.5723 +0000",
  "procRole" : "Foreground",
  "version" : 2,
  "userID" : 502,
  "deployVersion" : 210,
  "modelCode" : "MacBookPro12,1",
  "procStartAbsTime" : 17738278928446,
  "coalitionID" : 2116,
  "osVersion" : {
    "train" : "macOS 12.7.6",
    "build" : "21H1320",
    "releaseType" : "User"
  },
  "captureTime" : "2025-10-29 16:48:04.9644 +0000",
  "incident" : "6341A167-F974-4E34-8C29-E296F75A13BB",
  "bug_type" : "309",
  "pid" : 3557,
  "procExitAbsTime" : 17769644834183,
  "cpuType" : "X86-64",
  "procName" : "Python",
  "procPath" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/Resources\/Python.app\/Contents\/MacOS\/Python",
  "bundleInfo" : {"CFBundleShortVersionString":"3.13.6","CFBundleVersion":"3.13.6","CFBundleIdentifier":"org.python.python"},
  "storeInfo" : {"deviceIdentifierForVendor":"9A619145-9DF9-597B-B78E-3DFE42DD5498","thirdParty":true},
  "parentProc" : "Python",
  "parentPid" : 3398,
  "coalitionName" : "org.python.IDLE",
  "crashReporterKey" : "90C62505-A070-17C7-0B98-6C16CEF1F677",
  "responsiblePid" : 3398,
  "responsibleProc" : "Python",
  "wakeTime" : 814,
  "sleepWakeUUID" : "2459E341-1A8C-4234-858A-430599A5FE1B",
  "sip" : "enabled",
  "isCorpse" : 1,
  "exception" : {"codes":"0x0000000000000000, 0x0000000000000000","rawCodes":[0,0],"type":"EXC_CRASH","signal":"SIGABRT"},
  "asi" : {"libsystem_c.dylib":["abort() called"]},
  "asiBacktraces" : ["0   CoreFoundation                      0x00007ff812ea96e3 __exceptionPreprocess + 242\n1   libobjc.A.dylib                     0x00007ff812c098bb objc_exception_throw + 48\n2   CoreFoundation                      0x00007ff812ed1fc6 -[NSException raise] + 9\n3   AppKit                              0x00007ff815892c44 -[NSWindow(NSWindow_Theme) _postWindowNeedsToResetDragMarginsUnlessPostingDisabled] + 321\n4   AppKit                              0x00007ff81587ebf4 -[NSWindow _initContent:styleMask:backing:defer:contentView:] + 1288\n5   AppKit                              0x00007ff81587e6e6 -[NSWindow initWithContentRect:styleMask:backing:defer:] + 42\n6   AppKit                              0x00007ff815b5f627 -[NSWindow initWithContentRect:styleMask:backing:defer:screen:] + 50\n7   libqcocoa.dylib                     0x000000011186057f _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 247359\n8   libqcocoa.dylib                     0x0000000111835074 _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 69940\n9   libqcocoa.dylib                     0x000000011182c3eb _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 33963\n10  libqcocoa.dylib                     0x000000011182bce8 _ZN20QCocoaSystemTrayIcon13emitActivatedEv + 32168\n11  QtGui                               0x000000010f59a5b7 _ZN14QWindowPrivate6createEb + 471\n12  QtWidgets                           0x000000010eead285 _ZN14QWidgetPrivate6createEv + 1109\n13  QtWidgets                           0x000000010eeaa46e _ZN7QWidget6createEybb + 382\n14  QtWidgets                           0x000000010eec19a9 _ZN14QWidgetPrivate10setVisibleEb + 825\n15  QtWidgets                           0x000000010f0db4c2 _ZN14QDialogPrivate10setVisibleEb + 450\n16  QtWidgets.abi3.so                   0x000000010e9a68ae _ZN10sipQDialog10setVisibleEb + 110\n17  QtWidgets.abi3.so                   0x000000010eaa09e4 _ZL17meth_QDialog_openP7_objectS0_ + 148\n18  Python                              0x000000010b7b79fe cfunction_call + 110\n19  Python                              0x000000010b8f7067 _PyEval_EvalFrameDefault + 86743\n20  Python                              0x000000010b732004 method_vectorcall + 468\n21  Python                              0x000000010ba4b8e2 thread_run + 146\n22  Python                              0x000000010b9bb864 pythread_wrapper + 36\n23  libsystem_pthread.dylib             0x00007ff812d674e1 _pthread_start + 125\n24  libsystem_pthread.dylib             0x00007ff812d62f6b thread_start + 15"],
  "extMods" : {"caller":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"system":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"targeted":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"warnings":0},
  "lastExceptionBacktrace" : [{"imageOffset":1029843,"symbol":"__exceptionPreprocess","symbolLocation":226,"imageIndex":9},{"imageOffset":92347,"symbol":"objc_exception_throw","symbolLocation":48,"imageIndex":17},{"imageOffset":1195974,"symbol":"-[NSException raise]","symbolLocation":9,"imageIndex":9},{"imageOffset":420932,"symbol":"-[NSWindow(NSWindow_Theme) _postWindowNeedsToResetDragMarginsUnlessPostingDisabled]","symbolLocation":321,"imageIndex":11},{"imageOffset":338932,"symbol":"-[NSWindow _initContent:styleMask:backing:defer:contentView:]","symbolLocation":1288,"imageIndex":11},{"imageOffset":337638,"symbol":"-[NSWindow initWithContentRect:styleMask:backing:defer:]","symbolLocation":42,"imageIndex":11},{"imageOffset":3356199,"symbol":"-[NSWindow initWithContentRect:styleMask:backing:defer:screen:]","symbolLocation":50,"imageIndex":11},{"imageOffset":480639,"imageIndex":8},{"imageOffset":303220,"imageIndex":8},{"imageOffset":267243,"imageIndex":8},{"imageOffset":265448,"imageIndex":8},{"imageOffset":992695,"symbol":"QWindowPrivate::create(bool)","symbolLocation":471,"imageIndex":18},{"imageOffset":324229,"symbol":"QWidgetPrivate::create()","symbolLocation":1109,"imageIndex":6},{"imageOffset":312430,"symbol":"QWidget::create(unsigned long long, bool, bool)","symbolLocation":382,"imageIndex":6},{"imageOffset":407977,"symbol":"QWidgetPrivate::setVisible(bool)","symbolLocation":825,"imageIndex":6},{"imageOffset":2610370,"symbol":"QDialogPrivate::setVisible(bool)","symbolLocation":450,"imageIndex":6},{"imageOffset":1206446,"symbol":"sipQDialog::setVisible(bool)","symbolLocation":110,"imageIndex":7},{"imageOffset":2230756,"symbol":"meth_QDialog_open(_object*, _object*)","symbolLocation":148,"imageIndex":7},{"imageOffset":1145342,"symbol":"cfunction_call","symbolLocation":110,"imageIndex":2},{"imageOffset":2453607,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":86743,"imageIndex":2},{"imageOffset":598020,"symbol":"method_vectorcall","symbolLocation":468,"imageIndex":2},{"imageOffset":3848418,"symbol":"thread_run","symbolLocation":146,"imageIndex":2},{"imageOffset":3258468,"symbol":"pythread_wrapper","symbolLocation":36,"imageIndex":2},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}],
  "faultingThread" : 13,
  "threads" : [{"id":161071,"queue":"com.apple.main-thread","frames":[{"imageOffset":17322,"symbol":"__psynch_cvwait","symbolLocation":10,"imageIndex":0},{"imageOffset":27247,"symbol":"_pthread_cond_wait","symbolLocation":1249,"imageIndex":1},{"imageOffset":2869266,"symbol":"take_gil","symbolLocation":466,"imageIndex":2},{"imageOffset":3150605,"symbol":"_PyThreadState_Attach","symbolLocation":45,"imageIndex":2},{"imageOffset":3156224,"symbol":"PyGILState_Ensure","symbolLocation":48,"imageIndex":2},{"imageOffset":37777,"symbol":"sip_api_is_py_method_12_8","symbolLocation":65,"imageIndex":3},{"imageOffset":442908,"symbol":"sipQObject::eventFilter(QObject*, QEvent*)","symbolLocation":60,"imageIndex":4},{"imageOffset":630788,"symbol":"QCoreApplicationPrivate::sendThroughObjectEventFilters(QObject*, QEvent*)","symbolLocation":244,"imageIndex":5},{"imageOffset":56096,"symbol":"QApplicationPrivate::notify_helper(QObject*, QEvent*)","symbolLocation":288,"imageIndex":6},{"imageOffset":60150,"symbol":"QApplication::notify(QObject*, QEvent*)","symbolLocation":502,"imageIndex":6},{"imageOffset":1279205,"symbol":"sipQApplication::notify(QObject*, QEvent*)","symbolLocation":229,"imageIndex":7},{"imageOffset":632995,"symbol":"QCoreApplication::sendSpontaneousEvent(QObject*, QEvent*)","symbolLocation":147,"imageIndex":5},{"imageOffset":340483,"symbol":"QWidgetPrivate::drawWidget(QPaintDevice*, QRegion const&, QPoint const&, QFlags<QWidgetPrivate::DrawWidgetFlag>, QPainter*, QWidgetRepaintManager*)","symbolLocation":3987,"imageIndex":6},{"imageOffset":494366,"symbol":"QWidgetRepaintManager::paintAndFlush()","symbolLocation":5806,"imageIndex":6},{"imageOffset":495132,"symbol":"QWidgetRepaintManager::sync()","symbolLocation":268,"imageIndex":6},{"imageOffset":411664,"symbol":"QWidget::event(QEvent*)","symbolLocation":1632,"imageIndex":6},{"imageOffset":1365231,"symbol":"sipQWidget::event(QEvent*)","symbolLocation":191,"imageIndex":7},{"imageOffset":56116,"symbol":"QApplicationPrivate::notify_helper(QObject*, QEvent*)","symbolLocation":308,"imageIndex":6},{"imageOffset":60150,"symbol":"QApplication::notify(QObject*, QEvent*)","symbolLocation":502,"imageIndex":6},{"imageOffset":1279205,"symbol":"sipQApplication::notify(QObject*, QEvent*)","symbolLocation":229,"imageIndex":7},{"imageOffset":632739,"symbol":"QCoreApplication::sendEvent(QObject*, QEvent*)","symbolLocation":147,"imageIndex":5},{"imageOffset":634766,"symbol":"QCoreApplicationPrivate::sendPostedEvents(QObject*, int, QThreadData*)","symbolLocation":542,"imageIndex":5},{"imageOffset":99626,"imageIndex":8},{"imageOffset":104522,"imageIndex":8},{"imageOffset":524459,"symbol":"__CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__","symbolLocation":17,"imageIndex":9},{"imageOffset":524307,"symbol":"__CFRunLoopDoSource0","symbolLocation":180,"imageIndex":9},{"imageOffset":523661,"symbol":"__CFRunLoopDoSources0","symbolLocation":242,"imageIndex":9},{"imageOffset":518056,"symbol":"__CFRunLoopRun","symbolLocation":892,"imageIndex":9},{"imageOffset":515436,"symbol":"CFRunLoopRunSpecific","symbolLocation":562,"imageIndex":9},{"imageOffset":189926,"symbol":"RunCurrentEventLoopInMode","symbolLocation":292,"imageIndex":10},{"imageOffset":189258,"symbol":"ReceiveNextEventCommon","symbolLocation":594,"imageIndex":10},{"imageOffset":188645,"symbol":"_BlockUntilNextEventMatchingListInModeWithFilter","symbolLocation":70,"imageIndex":10},{"imageOffset":256681,"symbol":"_DPSNextEvent","symbolLocation":927,"imageIndex":11},{"imageOffset":250214,"symbol":"-[NSApplication(NSEvent) _nextEventMatchingEventMask:untilDate:inMode:dequeue:]","symbolLocation":1394,"imageIndex":11},{"imageOffset":194584,"symbol":"-[NSApplication run]","symbolLocation":586,"imageIndex":11},{"imageOffset":94313,"imageIndex":8},{"imageOffset":670854,"symbol":"QEventLoop::exec(QFlags<QEventLoop::ProcessEventsFlag>)","symbolLocation":534,"imageIndex":5},{"imageOffset":632043,"symbol":"QCoreApplication::exec()","symbolLocation":203,"imageIndex":5},{"imageOffset":2265164,"symbol":"meth_QApplication_exec(_object*, _object*)","symbolLocation":92,"imageIndex":7},{"imageOffset":1145342,"symbol":"cfunction_call","symbolLocation":110,"imageIndex":2},{"imageOffset":2418258,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":51394,"imageIndex":2},{"imageOffset":2358687,"symbol":"PyEval_EvalCode","symbolLocation":143,"imageIndex":2},{"imageOffset":2332753,"symbol":"builtin_exec","symbolLocation":449,"imageIndex":2},{"imageOffset":2432128,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":65264,"imageIndex":2},{"imageOffset":597769,"symbol":"method_vectorcall","symbolLocation":217,"imageIndex":2},{"imageOffset":2433382,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":66518,"imageIndex":2},{"imageOffset":2358687,"symbol":"PyEval_EvalCode","symbolLocation":143,"imageIndex":2},{"imageOffset":3162952,"symbol":"run_eval_code_obj","symbolLocation":136,"imageIndex":2},{"imageOffset":3161386,"symbol":"run_mod","symbolLocation":154,"imageIndex":2},{"imageOffset":3170626,"symbol":"_PyRun_SimpleStringFlagsWithName","symbolLocation":274,"imageIndex":2},{"imageOffset":3341383,"symbol":"Py_RunMain","symbolLocation":1031,"imageIndex":2},{"imageOffset":3347482,"symbol":"pymain_main","symbolLocation":378,"imageIndex":2},{"imageOffset":3347755,"symbol":"Py_BytesMain","symbolLocation":43,"imageIndex":2},{"imageOffset":21806,"symbol":"start","symbolLocation":462,"imageIndex":12}]},{"id":161075,"frames":[{"imageOffset":40218,"symbol":"__select","symbolLocation":10,"imageIndex":0},{"imageOffset":11826,"symbol":"select_select_impl","symbolLocation":450,"imageIndex":13},{"imageOffset":2431358,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":64494,"imageIndex":2},{"imageOffset":1465396,"symbol":"slot_tp_init","symbolLocation":340,"imageIndex":2},{"imageOffset":1405175,"symbol":"type_call","symbolLocation":135,"imageIndex":2},{"imageOffset":2418258,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":51394,"imageIndex":2},{"imageOffset":598020,"symbol":"method_vectorcall","symbolLocation":468,"imageIndex":2},{"imageOffset":3848418,"symbol":"thread_run","symbolLocation":146,"imageIndex":2},{"imageOffset":3258468,"symbol":"pythread_wrapper","symbolLocation":36,"imageIndex":2},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161076,"frames":[{"imageOffset":40218,"symbol":"__select","symbolLocation":10,"imageIndex":0},{"imageOffset":2020455,"imageIndex":14},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161090,"name":"Thread (pooled)","frames":[{"imageOffset":17322,"symbol":"__psynch_cvwait","symbolLocation":10,"imageIndex":0},{"imageOffset":27247,"symbol":"_pthread_cond_wait","symbolLocation":1249,"imageIndex":1},{"imageOffset":2442250,"imageIndex":5},{"imageOffset":2441892,"symbol":"QWaitCondition::wait(QMutex*, QDeadlineTimer)","symbolLocation":84,"imageIndex":5},{"imageOffset":2419147,"imageIndex":5},{"imageOffset":2384111,"imageIndex":5},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161091,"name":"Thread (pooled)","frames":[{"imageOffset":17322,"symbol":"__psynch_cvwait","symbolLocation":10,"imageIndex":0},{"imageOffset":27247,"symbol":"_pthread_cond_wait","symbolLocation":1249,"imageIndex":1},{"imageOffset":2442250,"imageIndex":5},{"imageOffset":2441892,"symbol":"QWaitCondition::wait(QMutex*, QDeadlineTimer)","symbolLocation":84,"imageIndex":5},{"imageOffset":2419147,"imageIndex":5},{"imageOffset":2384111,"imageIndex":5},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161092,"name":"Thread (pooled)","frames":[{"imageOffset":17322,"symbol":"__psynch_cvwait","symbolLocation":10,"imageIndex":0},{"imageOffset":27247,"symbol":"_pthread_cond_wait","symbolLocation":1249,"imageIndex":1},{"imageOffset":2442250,"imageIndex":5},{"imageOffset":2441892,"symbol":"QWaitCondition::wait(QMutex*, QDeadlineTimer)","symbolLocation":84,"imageIndex":5},{"imageOffset":2419147,"imageIndex":5},{"imageOffset":2384111,"imageIndex":5},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161093,"name":"Thread (pooled)","frames":[{"imageOffset":17322,"symbol":"__psynch_cvwait","symbolLocation":10,"imageIndex":0},{"imageOffset":27247,"symbol":"_pthread_cond_wait","symbolLocation":1249,"imageIndex":1},{"imageOffset":2442250,"imageIndex":5},{"imageOffset":2441892,"symbol":"QWaitCondition::wait(QMutex*, QDeadlineTimer)","symbolLocation":84,"imageIndex":5},{"imageOffset":2419147,"imageIndex":5},{"imageOffset":2384111,"imageIndex":5},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161094,"frames":[{"imageOffset":8008,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":1}]},{"id":161095,"name":"com.apple.NSEventThread","frames":[{"imageOffset":6458,"symbol":"mach_msg_trap","symbolLocation":10,"imageIndex":0},{"imageOffset":7336,"symbol":"mach_msg","symbolLocation":56,"imageIndex":0},{"imageOffset":524957,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":319,"imageIndex":9},{"imageOffset":518440,"symbol":"__CFRunLoopRun","symbolLocation":1276,"imageIndex":9},{"imageOffset":515436,"symbol":"CFRunLoopRunSpecific","symbolLocation":562,"imageIndex":9},{"imageOffset":1754482,"symbol":"_NSEventThread","symbolLocation":132,"imageIndex":11},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]},{"id":161245,"frames":[{"imageOffset":8008,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":1}]},{"id":161246,"frames":[{"imageOffset":8008,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":1}]},{"id":161316,"frames":[{"imageOffset":8008,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":1}]},{"id":161318,"frames":[{"imageOffset":8008,"symbol":"start_wqthread","symbolLocation":0,"imageIndex":1}]},{"triggered":true,"id":161328,"threadState":{"r13":{"value":206158430216},"rax":{"value":0},"rflags":{"value":582},"cpu":{"value":0},"r14":{"value":6},"rsi":{"value":6},"r8":{"value":123145489361488},"cr2":{"value":0},"rdx":{"value":0},"r10":{"value":0},"r9":{"value":140703444393883},"r15":{"value":22},"rbx":{"value":123145489371136},"trap":{"value":133},"err":{"value":33554760},"r11":{"value":582},"rip":{"value":140703444438990,"matchesCrashFrame":1},"rbp":{"value":123145489361840},"rsp":{"value":123145489361800},"r12":{"value":48659},"rcx":{"value":123145489361800},"flavor":"x86_THREAD_STATE","rdi":{"value":48659}},"frames":[{"imageOffset":32718,"symbol":"__pthread_kill","symbolLocation":10,"imageIndex":0},{"imageOffset":25087,"symbol":"pthread_kill","symbolLocation":263,"imageIndex":1},{"imageOffset":531732,"symbol":"abort","symbolLocation":123,"imageIndex":15},{"imageOffset":65666,"symbol":"abort_message","symbolLocation":241,"imageIndex":16},{"imageOffset":4701,"symbol":"demangling_terminate_handler()","symbolLocation":266,"imageIndex":16},{"imageOffset":122425,"symbol":"_objc_terminate()","symbolLocation":96,"imageIndex":17},{"imageOffset":62631,"symbol":"std::__terminate(void (*)())","symbolLocation":8,"imageIndex":16},{"imageOffset":72965,"symbol":"__cxxabiv1::failed_throw(__cxxabiv1::__cxa_exception*)","symbolLocation":27,"imageIndex":16},{"imageOffset":72908,"symbol":"__cxa_throw","symbolLocation":116,"imageIndex":16},{"imageOffset":92601,"symbol":"objc_exception_throw","symbolLocation":302,"imageIndex":17},{"imageOffset":1195974,"symbol":"-[NSException raise]","symbolLocation":9,"imageIndex":9},{"imageOffset":420932,"symbol":"-[NSWindow(NSWindow_Theme) _postWindowNeedsToResetDragMarginsUnlessPostingDisabled]","symbolLocation":321,"imageIndex":11},{"imageOffset":338932,"symbol":"-[NSWindow _initContent:styleMask:backing:defer:contentView:]","symbolLocation":1288,"imageIndex":11},{"imageOffset":337638,"symbol":"-[NSWindow initWithContentRect:styleMask:backing:defer:]","symbolLocation":42,"imageIndex":11},{"imageOffset":3356199,"symbol":"-[NSWindow initWithContentRect:styleMask:backing:defer:screen:]","symbolLocation":50,"imageIndex":11},{"imageOffset":480639,"imageIndex":8},{"imageOffset":303220,"imageIndex":8},{"imageOffset":267243,"imageIndex":8},{"imageOffset":265448,"imageIndex":8},{"imageOffset":992695,"symbol":"QWindowPrivate::create(bool)","symbolLocation":471,"imageIndex":18},{"imageOffset":324229,"symbol":"QWidgetPrivate::create()","symbolLocation":1109,"imageIndex":6},{"imageOffset":312430,"symbol":"QWidget::create(unsigned long long, bool, bool)","symbolLocation":382,"imageIndex":6},{"imageOffset":407977,"symbol":"QWidgetPrivate::setVisible(bool)","symbolLocation":825,"imageIndex":6},{"imageOffset":2610370,"symbol":"QDialogPrivate::setVisible(bool)","symbolLocation":450,"imageIndex":6},{"imageOffset":1206446,"symbol":"sipQDialog::setVisible(bool)","symbolLocation":110,"imageIndex":7},{"imageOffset":2230756,"symbol":"meth_QDialog_open(_object*, _object*)","symbolLocation":148,"imageIndex":7},{"imageOffset":1145342,"symbol":"cfunction_call","symbolLocation":110,"imageIndex":2},{"imageOffset":2453607,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":86743,"imageIndex":2},{"imageOffset":598020,"symbol":"method_vectorcall","symbolLocation":468,"imageIndex":2},{"imageOffset":3848418,"symbol":"thread_run","symbolLocation":146,"imageIndex":2},{"imageOffset":3258468,"symbol":"pythread_wrapper","symbolLocation":36,"imageIndex":2},{"imageOffset":25825,"symbol":"_pthread_start","symbolLocation":125,"imageIndex":1},{"imageOffset":8043,"symbol":"thread_start","symbolLocation":15,"imageIndex":1}]}],
  "usedImages" : [
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 140703444406272,
    "size" : 229376,
    "uuid" : "2fe67e94-4a5e-3506-9e02-502f7270f7ef",
    "path" : "\/usr\/lib\/system\/libsystem_kernel.dylib",
    "name" : "libsystem_kernel.dylib"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 140703444635648,
    "size" : 49152,
    "uuid" : "5a5f7316-85b7-315e-baf3-76211ee65604",
    "path" : "\/usr\/lib\/system\/libsystem_pthread.dylib",
    "name" : "libsystem_pthread.dylib"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4486463488,
    "CFBundleShortVersionString" : "3.13.6, (c) 2001-2024 Python Software Foundation.",
    "CFBundleIdentifier" : "org.python.python",
    "size" : 4943872,
    "uuid" : "3e3e51d1-06ad-3908-8a89-b57769b0eb3d",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/Python",
    "name" : "Python",
    "CFBundleVersion" : "3.13.6"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4482560000,
    "size" : 90112,
    "uuid" : "3c3502c7-dcd4-34eb-b1ff-63106cb62a4e",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/sip.cpython-313-darwin.so",
    "name" : "sip.cpython-313-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4567080960,
    "size" : 1777664,
    "uuid" : "48217fd0-a431-3edf-ac4c-834e19c03d50",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/QtCore.abi3.so",
    "name" : "QtCore.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4560715776,
    "size" : 5464064,
    "uuid" : "5dd15e14-a793-339f-b921-6bb4cd992e77",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/Qt6\/lib\/QtCore.framework\/Versions\/A\/QtCore",
    "name" : "QtCore"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4544913408,
    "size" : 5152768,
    "uuid" : "bc196354-97c2-3137-9f3d-e44718bd0753",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/Qt6\/lib\/QtWidgets.framework\/Versions\/A\/QtWidgets",
    "name" : "QtWidgets"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4538761216,
    "size" : 2875392,
    "uuid" : "ae8322b3-396f-3aed-8d75-b1ba17c952ee",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/QtWidgets.abi3.so",
    "name" : "QtWidgets.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4588482560,
    "size" : 700416,
    "uuid" : "70a50108-a972-33e4-9472-85b1c247086f",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/Qt6\/plugins\/platforms\/libqcocoa.dylib",
    "name" : "libqcocoa.dylib"
  },
  {
    "source" : "P",
    "arch" : "x86_64h",
    "base" : 140703444951040,
    "CFBundleShortVersionString" : "6.9",
    "CFBundleIdentifier" : "com.apple.CoreFoundation",
    "size" : 5255168,
    "uuid" : "fdd28505-5456-3c40-a5ba-7890b064db39",
    "path" : "\/System\/Library\/Frameworks\/CoreFoundation.framework\/Versions\/A\/CoreFoundation",
    "name" : "CoreFoundation",
    "CFBundleVersion" : "1866"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 140703592808448,
    "CFBundleShortVersionString" : "2.1.1",
    "CFBundleIdentifier" : "com.apple.HIToolbox",
    "size" : 3096576,
    "uuid" : "913d3d2e-4e4c-3907-98fe-8f4abd551297",
    "path" : "\/System\/Library\/Frameworks\/Carbon.framework\/Versions\/A\/Frameworks\/HIToolbox.framework\/Versions\/A\/HIToolbox",
    "name" : "HIToolbox"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 140703489507328,
    "CFBundleShortVersionString" : "6.9",
    "CFBundleIdentifier" : "com.apple.AppKit",
    "size" : 15269888,
    "uuid" : "5dd484cf-ed6a-3633-b42e-6518aeecd5b9",
    "path" : "\/System\/Library\/Frameworks\/AppKit.framework\/Versions\/C\/AppKit",
    "name" : "AppKit",
    "CFBundleVersion" : "2113.65.150"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4616978432,
    "size" : 442368,
    "uuid" : "eea022bb-a6ab-3cd1-8ac1-54ce8cfd3333",
    "path" : "\/usr\/lib\/dyld",
    "name" : "dyld"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4478763008,
    "size" : 20480,
    "uuid" : "4467f668-cf5f-3afb-9a37-f1c19b65e194",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/lib-dynload\/select.cpython-313-darwin.so",
    "name" : "select.cpython-313-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4482719744,
    "CFBundleShortVersionString" : "8.6.16",
    "CFBundleIdentifier" : "com.tcltk.tcllibrary",
    "size" : 2207744,
    "uuid" : "59d3fb5b-ac36-38c1-9d76-61d1c534290a",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/Frameworks\/Tcl.framework\/Versions\/8.6\/Tcl",
    "name" : "Tcl",
    "CFBundleVersion" : "8.6.16"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 140703443390464,
    "size" : 561152,
    "uuid" : "202d7260-ea46-3956-a471-19c9bcf45274",
    "path" : "\/usr\/lib\/system\/libsystem_c.dylib",
    "name" : "libsystem_c.dylib"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 140703444316160,
    "size" : 90112,
    "uuid" : "69ac868b-1157-364a-984a-5ef26973f661",
    "path" : "\/usr\/lib\/libc++abi.dylib",
    "name" : "libc++abi.dylib"
  },
  {
    "source" : "P",
    "arch" : "x86_64h",
    "base" : 140703443136512,
    "size" : 241664,
    "uuid" : "b36a2b52-68a9-3e44-b927-71c24be1272f",
    "path" : "\/usr\/lib\/libobjc.A.dylib",
    "name" : "libobjc.A.dylib"
  },
  {
    "source" : "P",
    "arch" : "x86_64",
    "base" : 4551507968,
    "size" : 7868416,
    "uuid" : "8c94e242-8015-33e9-83b8-9ea4af68851e",
    "path" : "\/Library\/Frameworks\/Python.framework\/Versions\/3.13\/lib\/python3.13\/site-packages\/PyQt6\/Qt6\/lib\/QtGui.framework\/Versions\/A\/QtGui",
    "name" : "QtGui"
  }
],
  "sharedCache" : {
  "base" : 140703441375232,
  "size" : 19331678208,
  "uuid" : "246818c3-4b9f-3462-bcaf-fdf71975e5fe"
},
  "vmSummary" : "ReadOnly portion of Libraries: Total=1.0G resident=0K(0%) swapped_out_or_unallocated=1.0G(100%)\nWritable regions: Total=740.1M written=0K(0%) resident=0K(0%) swapped_out=0K(0%) unallocated=740.1M(100%)\n\n                                VIRTUAL   REGION \nREGION TYPE                        SIZE    COUNT (non-coalesced) \n===========                     =======  ======= \nAccelerate framework               128K        1 \nActivity Tracing                   256K        1 \nCG backing stores                 1920K        4 \nColorSync                          224K       26 \nCoreAnimation                       56K        6 \nCoreGraphics                        12K        2 \nCoreUI image data                  792K        5 \nFoundation                          16K        1 \nKernel Alloc Once                    8K        1 \nMALLOC                           282.6M      104 \nMALLOC guard page                   32K        8 \nMALLOC_LARGE (reserved)            384K        1         reserved VM address space (unallocated)\nMALLOC_NANO (reserved)           384.0M        1         reserved VM address space (unallocated)\nSTACK GUARD                         56K       14 \nStack                             53.2M       15 \nVM_ALLOCATE                       17.1M       38 \n__CTF                               756        1 \n__DATA                            26.1M      510 \n__DATA_CONST                      23.6M      293 \n__DATA_DIRTY                      1388K      169 \n__FONT_DATA                          4K        1 \n__LINKEDIT                       661.1M       87 \n__OBJC_RO                         82.9M        1 \n__OBJC_RW                         3200K        2 \n__TEXT                           392.7M      518 \n__UNICODE                          592K        1 \ndyld private memory               1024K        1 \nmapped file                      393.2M       54 \nshared memory                      768K       15 \n===========                     =======  ======= \nTOTAL                              2.3G     1881 \nTOTAL, minus reserved VM space     1.9G     1881 \n",
  "legacyInfo" : {
  "threadTriggered" : {

  }
},
  "trialInfo" : {
  "rollouts" : [
    {
      "rolloutId" : "6112e14f37f5d11121dcd519",
      "factorPackIds" : {
        "SIRI_TEXT_TO_SPEECH" : "634710168e8be655c1316aaa"
      },
      "deploymentId" : 240000231
    },
    {
      "rolloutId" : "5fb4245a1bbfe8005e33a1e1",
      "factorPackIds" : {

      },
      "deploymentId" : 240000021
    }
  ],
  "experiments" : [

  ]
}
}

