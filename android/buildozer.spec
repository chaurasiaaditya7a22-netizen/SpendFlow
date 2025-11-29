[app]

title = Spend Flow
package.name = spendflow
package.domain = com.adityaspendflow
source.dir = ..
source.include_exts = py,png,jpg,kv,ini
version = 1.0.0

requirements = python3,kivy
orientation = portrait

fullscreen = 0

icon.filename = ../image-38.png

[buildozer]

log_level = 2
warn_on_root = 1
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

android.filename = SpendFlow.apk
