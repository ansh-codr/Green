# Prompt log

| Prompt | AI got wrong / limitation | Fix |
|---|---|---|
| Build GREEN from the attached brief. | Original implementation used Python and local-only data. | Rebuilt frontend in React and began migration to Firebase/Vercel. |
| Make an animated React project and Android APK. | Android build could not download Gradle and the environment has no Android SDK; no APK was produced. | Added Capacitor project and build instructions; build and verify on an Android Studio machine. |
| Use the specified Firebase stack and make it deployable. | Integration and all requested features could not be verified without configuration; trust, chat, robust filtering and other production requirements remain incomplete. | Configure and test Firebase; complete and review missing features before production. |
