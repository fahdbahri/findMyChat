export function GoogleOAuth() {
  const handleGoogleLogin = () => {
    const API_URL = import.meta.env.VITE_API_URL;
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      new URLSearchParams({
        client_id: import.meta.env.VITE_REACT_APP_CLIENT_ID,
        redirect_uri: `${API_URL}/auth/callback`,
        response_type: 'code',
        scope: 'openid email profile https://www.googleapis.com/auth/gmail.readonly',
        access_type: 'offline',
      });

    window.location.href = authUrl;
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <button
        onClick={handleGoogleLogin}
        className="bg-blue-800 text-white px-6 py-3 rounded-full flex items-center gap-2 cursor-pointer"
      >
        <img src="https://www.google.com/favicon.ico" alt="Google" className="w-5 h-5" />
        Sign in with Google
      </button>
    </div>
  );
}
