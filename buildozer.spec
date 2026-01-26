[app]
title = Hohenmessung Kamera
package.name = hohenmessung_kamera
package.domain = org.example

source.dir = .
source.include_exts = py,kv,png,jpg

version = 0.1
requirements = python3,kivy,cython

p4a.requirements = python3,kivy,android

android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b

android.enable_androidx = True

p4a.branch = master

# garden requirement
p4a.local_recipes = ./recipes
