[app]
<<<<<<< HEAD
title = Höhenmessung
package.name = hohenmessung
=======
title = Photo Capture
package.name = photocapture
>>>>>>> a11696d3c0430c7b48fa896d82828694f4b7fc6b
package.domain = org.example

icon.filename = %(source.dir)s/icons/camera_red.png
source.dir = .
<<<<<<< HEAD
source.include_exts = py,png,jpg,kv,atlas,json
icon.filename = %(source.dir)s/icons/camera_red.png
=======
source.include_exts = py,png,jpg,kv,atlas
>>>>>>> a11696d3c0430c7b48fa896d82828694f4b7fc6b

version = 0.1

requirements = python3,kivy,camera4kivy,gestures4kivy

orientation = portrait, landscape, portrait-reverse, landscape-reverse
fullscreen = 0
android.permissions = CAMERA, RECORD_AUDIO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.enable_androidx = True
android.archs = arm64-v8a
android.allow_backup = True

p4a.hook = camerax_provider/gradle_options.py

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1