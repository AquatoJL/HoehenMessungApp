[app]
title = Kamera App
package.name = camera
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.2
requirements = python3,kivy,plyer

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = main
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,VIBRATE,INTERNET

android.api = 33
android.minapi = 21
android.ndk = 25b

android.accept_sdk_license = True
android.enable_androidx = True
