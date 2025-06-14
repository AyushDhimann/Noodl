# 🍜 noodl.

A **Web3-enabled learning app** that gamifies your journey through knowledge. Log in securely using MetaMask or your wallet address and start earning NFT trophies as proof of learning.

---

## 🚀 Features

- 🔐 **Web3 Login via MetaMask**
  - WalletConnect v2 integration
  - Works on Android (14 or lower) and iOS
- 🧱 **Manual Wallet Address Login**
  - Legacy login option for Android 15+ where MetaMask is unsupported
- 📱 **Gamified Learning Experience**
  - Learn and earn NFT-based trophies as credentials
- 📦 **Session Persistence**
  - Persists wallet session using `SharedPreferences`
- 🎨 **Custom Theming**
  - Uses custom fonts
  - Rich UI with animated elements, gradients, and SVG branding

---

## 📸 Screenshots

---

## 🛠️ Tech Stack

- **Flutter** (Stable Channel)
- **Provider** for state management
- **WalletConnect v2 + MetaMask** for Web3 login
- **SharedPreferences** for persistent sessions
- **Custom theming** with gradients, fonts, and dark mode support

---

## 🧪 How to Run

1. **Clone the repo:**

```bash
git clone https://github.com/your-username/noodl.git
cd noodl/src/frontend
```

2. **Install Dependencies:**

```bash
flutter pub get
```

3. **Run the app:**

```bash
flutter run
```
Make sure your emulator or connected device supports Web3-compatible browsers for MetaMask login.

## ⚠️ Notes

* **Android 15+** blocks MetaMask’s WebView connection. Users on these versions must use the **manual wallet login** option.
* If testing MetaMask login, ensure the MetaMask extension is installed and you're using a supported browser (e.g., Chrome).

