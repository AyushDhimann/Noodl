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

# Environment Configuration Example

This document explains the purpose and usage of the environment configuration file for your Flutter project.

## File Location

The example file is located at:  
**`constants/env_example.dart`**

## Purpose

This file contains various environment-specific constants such as API endpoints, contract addresses, and keys for external services (e.g., Microsoft Azure, WalletConnect). It serves as a template for developers to create their own local `env.dart` file. **Important:** Do **not** commit your actual environment file (with real keys or sensitive data) to version control.

## Example Contents

Below is an example template for `env_example.dart`:

```dart
// constants/env_example.dart

/// Example environment configuration file for the Flutter project.
///
/// Rename this file to `env.dart` and insert your actual configuration values.
/// **WARNING:** Do not commit your `env.dart` with real credentials to your repository.

/// Base URL for your API endpoints.
const String baseURL = 'https://your-api-base-url.com';

/// Microsoft subscription key for accessing Azure services.
const String msSubsKey = 'your-microsoft-subscription-key';

/// Microsoft Speech Region (optional)  
/// For example: "eastus", "westeurope", etc.
const String msSpeechRegion = 'your-speech-region';


```
---

## 📸 Screenshots

| | | | |
|---|---|---|---|
| ![IMG_9733](https://github.com/user-attachments/assets/72793115-3fa5-4130-a108-cd7fc29738c1) | ![IMG_9734](https://github.com/user-attachments/assets/dafffa0d-ec68-493b-af08-69d6624aaddb) | ![IMG_9735](https://github.com/user-attachments/assets/de820a41-38ac-440f-9c40-9afc6c68f6ea) | ![IMG_9736](https://github.com/user-attachments/assets/98135719-1088-4bf4-af15-063df8644a28) |
| ![IMG_9737](https://github.com/user-attachments/assets/69bac1cd-65bb-46ad-a061-5eafc809eaca) | ![IMG_9738](https://github.com/user-attachments/assets/c8ffc3ff-e134-41a1-ba23-edf2589f7ecc) | ![IMG_9739](https://github.com/user-attachments/assets/895ea187-fcc4-4240-9460-1f6835e74890) | ![IMG_9740](https://github.com/user-attachments/assets/4e642a88-0c9e-453e-bc2a-d9d89d8de0f7) |
| ![IMG_9741](https://github.com/user-attachments/assets/148c158b-1506-40d0-9d47-663cfc673d89) | ![IMG_9742](https://github.com/user-attachments/assets/ea31654e-f207-4b51-bff9-fae1872bc122) | ![IMG_9743](https://github.com/user-attachments/assets/8de88363-512c-4f88-88c9-c588a9325164) | ![IMG_9744](https://github.com/user-attachments/assets/3a703b17-02f6-47f7-9df3-d0340cdc4388) |
| ![IMG_9745](https://github.com/user-attachments/assets/51af8f37-c2f3-40c9-9ba6-21c9568cebaf) | ![IMG_9793](https://github.com/user-attachments/assets/e70b19de-bf05-4f7d-9379-2c69db196db0) | ![IMG_9747](https://github.com/user-attachments/assets/025c6985-24be-446f-a7c5-a5fb93d35645) | ![IMG_9748](https://github.com/user-attachments/assets/05f206e9-bb57-453b-8c0f-195ac49edbe8) |
| ![IMG_9749](https://github.com/user-attachments/assets/752cad0a-c406-405a-9224-a49c85399d8b) | ![IMG_9792](https://github.com/user-attachments/assets/91ca2e99-11a1-4135-b61c-9414e8a2d5de) | ![IMG_9751](https://github.com/user-attachments/assets/c340cedb-ec5f-4ef9-ba67-990b102b4442) | ![IMG_9752](https://github.com/user-attachments/assets/a5a457ed-6c59-41d4-b1ab-b2091ffcd647) |
| ![IMG_9753](https://github.com/user-attachments/assets/19d9077c-d9e4-4e95-a3cc-67cf8fe2b5d4) | ![IMG_9754](https://github.com/user-attachments/assets/8c899b0c-efd9-4d70-a9f9-22089f9f437c) | ![IMG_9755](https://github.com/user-attachments/assets/126ea2f5-8f9b-4d77-a2ae-179348de3437) | ![IMG_9756](https://github.com/user-attachments/assets/823f6eda-1282-457b-abed-d4c638a2a0bb) |
| ![IMG_9757](https://github.com/user-attachments/assets/dd576fab-74e1-4758-92a9-0351337a63f4) | ![IMG_9758](https://github.com/user-attachments/assets/f345bf7d-c6e8-4e6c-bdbf-ff1587020181) | ![IMG_9759](https://github.com/user-attachments/assets/bddfc52a-9952-4999-8ddf-24da8a97863f) | ![IMG_9760](https://github.com/user-attachments/assets/b194f4ce-521c-4393-a33b-786c7e294aa0) |
| ![IMG_9761](https://github.com/user-attachments/assets/e4c40d00-3ae2-45ba-a20f-366ffb8ad5a3) | ![IMG_9762](https://github.com/user-attachments/assets/b8d4f4e3-0f37-4879-ad3d-ec53b53c57cd) | ![IMG_9763](https://github.com/user-attachments/assets/de2b306d-865b-4b29-9091-5d6a23492947) | ![IMG_9764](https://github.com/user-attachments/assets/0a2e1ea5-8757-4598-86b8-535f743ffffe) |




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

