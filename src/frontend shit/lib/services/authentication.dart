import 'package:google_sign_in/google_sign_in.dart';
import 'package:firebase_auth/firebase_auth.dart';

class AuthService {
  Future<UserCredential?> signInWithGoogle() async {
    try {
      // Begin the interactive sign-in process
      final GoogleSignInAccount? gUser = await GoogleSignIn().signIn();

      // Handle case when user cancels sign-in
      if (gUser == null) {
        print("Sign-in aborted by user.");
        return null;
      }

      // Obtain the auth details from the request
      final GoogleSignInAuthentication gAuth = await gUser.authentication;

      // Create a credential from the authentication
      final credential = GoogleAuthProvider.credential(
        accessToken: gAuth.accessToken,
        idToken: gAuth.idToken,
      );

      // Sign in to Firebase with the credential
      return await FirebaseAuth.instance.signInWithCredential(credential);
    } catch (e) {
      print("Error during Google sign-in: $e");
      return null;
    }
  }
}
