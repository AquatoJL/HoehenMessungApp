[app]
title = Höhenmessung
package.name = measure
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
icon.filename = %(source.dir)s/icons/appIcon.png

version = 1.0

requirements = python3,kivy,kivymd,camera4kivy,gestures4kivy,plyer,android

orientation = landscape
fullscreen = 0

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
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
