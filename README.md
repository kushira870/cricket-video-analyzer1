# Cricket Video Analyzer (Flutter starter)

## Setup
1. Install Flutter SDK, Android Studio and Android SDK; run `flutter doctor`.
2. Run `flutter create cricket_video_analyzer` in a separate folder.
3. Replace the generated `lib/main.dart` and `pubspec.yaml` with the files in this package.
4. Run `flutter pub get` and `flutter run` with an Android phone attached (USB debugging enabled) or emulator.
5. Run `flutter build apk --release`; find APK at `build/app/outputs/flutter-apk/app-release.apk`.

## Features
- Import local video using Android's picker
- Play/pause, seek, approximate 100ms steps, 0.25x/0.5x/1x playback
- Batting and bowling coaching notes
- Manually tap and connect ball locations; save/load one session

## Limitations
This is starter source, not a prebuilt or device-tested APK. No AI detection, automatic biomechanics, or automatic ball tracking. Player video files may be temporary picker paths and may not survive cleanup. Save/load stores only the most recent session, not a database. Tracking is normalized to the video frame and represents manual annotations, not measured trajectory. Some devices/codecs may not support all playback speeds. Seek is approximate and not guaranteed frame accurate.
