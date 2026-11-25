# GREEN · Second Life

React/Vite marketplace with Firebase auth, Firestore, Storage, Vercel API functions, PWA and Capacitor Android project. Work in progress: do not treat as production-ready until the limitations below are resolved and real Firebase integration tested.

## Setup

1. Install Node.js 20 or newer. Run `npm install`.
2. Copy `.env.example` to `.env` and fill Firebase web values and Firebase Admin service account fields. Never commit `.env` or the private key.
3. Enable Google and Anonymous authentication; add your local and hosted domains to Firebase Auth's authorized domains. Create Firestore and Storage. Deploy `firestore.rules` and `storage.rules` with Firebase CLI after reviewing them.
4. Run `npm run seed` to write 200 fictional sales and category models. This replaces seed documents with the same deterministic IDs; use a development project.
5. For local API routes, use `npx vercel dev` (plain `npm run dev` serves only Vite). Ensure server environment variables are available to Vercel CLI.
6. Deploy: `npm install -g vercel`, `vercel login`, `vercel`, then configure all variables in the Vercel project settings and run `vercel --prod`. Set `ALLOWED_ORIGINS` to comma-separated trusted app origins.
7. Android: set `VITE_API_BASE_URL` to the deployed HTTPS URL in `.env`, `npm run android:sync`, `npm run android:open`; in Android Studio install the SDK and build the debug APK. Or run `cd android && ./gradlew assembleDebug` (Windows: `gradlew.bat assembleDebug`). APK path: `android/app/build/outputs/apk/debug/app-debug.apk`.

## Pricing

The seed generates 200 fictional records. For each category it fits `ln(sold/original) = condition intercept + shared age slope`, with group-centered least squares. Suggested ranges are illustrative ±10%, not confidence intervals. Synthetic data encodes assumed depreciation and cannot establish market price or real-world trends. An illustrative generator assumption is that calculators lose roughly 9.5% of retained value per year; the seed fits a slightly different value due to random variation and rounding.

## Limitations

Firebase-dependent calls, authentication, uploads, seeding and Vercel deployment require your own configured project and have not been verified here. Firestore queries involving multiple filters and creation time may need composite indexes. Filtering and search are applied to each fetched page, so pages may be sparse and search does not cover the whole collection in one request. Marketplace listings are public; offers are restricted to participants. Anonymous account upgrades/merges, completed deal verification, trust badges, offers inbox, chat, comprehensive moderation, comprehensive security review, robust offline mutations, full accessibility, all requested visual assets and several requested animations are not implemented. Rate limits use Firestore counters and depend on trusted proxy IP headers; configure TTL cleanup for `_rate_limits.expiresAt` and production edge protections. The APK build could not run in this environment because Android SDK and Gradle downloads were unavailable. Do not publish for real users without addressing and testing these issues.
