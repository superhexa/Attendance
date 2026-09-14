import React, { useState } from "react";
import { useNavigate, useLocation, Navigate, Link } from "react-router-dom";
import { School, Loader2, ShieldCheck, Mail, Lock, Sparkles, ArrowLeft } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { useLang } from "@/lib/i18n";
import { apiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";

export default function Login() {
  const { t, lang, toggle } = useLang();
  const { user, login, verify2fa } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [twofa, setTwofa] = useState(null);
  const [otp, setOtp] = useState("");

  if (user && user.id) return <Navigate to="/dashboard" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await login(email, password, remember);
      if (res.requires_2fa) {
        setTwofa(res.user_id);
      } else {
        navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
      }
    } catch (err) {
      console.error("Login error", err, err?.response);
      let msg;
      if (err?.response?.data?.detail) {
        msg = apiError(err);
      } else if (err?.code === "ERR_NETWORK" || err?.message === "Network Error") {
        msg = lang === "ar"
          ? "تعذّر الاتصال بالخادم. تأكد من الاتصال بالإنترنت ثم أعد المحاولة."
          : "Cannot reach the server. Check your connection and try again.";
      } else if (err?.response?.status >= 500) {
        msg = lang === "ar"
          ? "خطأ في الخادم. يرجى المحاولة بعد قليل."
          : "Server error. Please try again shortly.";
      } else {
        msg = lang === "ar" ? "تعذّر تسجيل الدخول. تأكد من البريد وكلمة المرور." : "Login failed. Check your email and password.";
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const submitOtp = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await verify2fa(twofa, otp);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(apiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-50" dir={lang === "ar" ? "rtl" : "ltr"}>
      {/* Decorative background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 start-1/4 h-96 w-96 rounded-full bg-emerald-200/50 blur-3xl" />
        <div className="absolute top-40 end-0 h-80 w-80 rounded-full bg-amber-200/40 blur-3xl" />
        <div className="absolute bottom-0 start-0 h-72 w-72 rounded-full bg-teal-200/40 blur-3xl" />
        <div className="absolute inset-0" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, rgba(15,76,58,0.06) 1px, transparent 0)", backgroundSize: "28px 28px" }} />
      </div>

      <div className="relative mx-auto flex min-h-screen max-w-6xl items-center justify-center px-4 py-10 sm:px-6">
        <div className="w-full max-w-md">
          {/* Top nav */}
          <div className="mb-6 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 text-sm font-bold text-slate-700 hover:text-emerald-700">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-lg shadow-emerald-600/25">
                <School className="h-5 w-5" />
              </div>
              <span className="hidden sm:inline">{t("app_name")}</span>
            </Link>
            <button onClick={toggle} className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-bold text-slate-700 hover:bg-slate-100" data-testid="login-lang-toggle">
              {lang === "ar" ? "English" : "العربية"}
            </button>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-2xl shadow-slate-900/10 backdrop-blur-xl sm:p-10">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
              <Sparkles className="h-3.5 w-3.5" /> {t("app_name")}
            </span>
            <h1 className="mt-4 text-2xl font-extrabold text-slate-900 sm:text-3xl">{t("login")}</h1>
            <p className="mt-1 text-sm text-slate-600">{t("login_subtitle")}</p>

            {error && (
              <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700" data-testid="login-error">
                {error}
              </div>
            )}

            {!twofa ? (
              <form onSubmit={submit} className="mt-6 space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="email" className="flex items-center gap-2 text-slate-700">
                    <Mail className="h-4 w-4 text-emerald-600" />
                    {t("email")}
                  </Label>
                  <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@school.edu" data-testid="login-email" autoComplete="email" />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="password" className="flex items-center gap-2 text-slate-700">
                    <Lock className="h-4 w-4 text-emerald-600" />
                    {t("password")}
                  </Label>
                  <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••" data-testid="login-password" autoComplete="current-password" />
                </div>
                <label className="flex items-center gap-2 text-sm text-slate-600">
                  <Checkbox checked={remember} onCheckedChange={(v) => setRemember(!!v)} data-testid="login-remember" />
                  {t("remember_me")}
                </label>
                <Button type="submit" size="lg" className="w-full gap-2 rounded-xl bg-emerald-600 font-bold shadow-lg shadow-emerald-600/25 hover:bg-emerald-700"
                  disabled={loading} data-testid="login-submit">
                  {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> {t("signing_in")}</>
                    : <>{t("login")} <ArrowLeft className={lang === "ar" ? "h-5 w-5" : "h-5 w-5 rotate-180"} /></>}
                </Button>
              </form>
            ) : (
              <form onSubmit={submitOtp} className="mt-6 space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="otp" className="flex items-center gap-2 text-slate-700">
                    <ShieldCheck className="h-4 w-4 text-emerald-600" />
                    {lang === "ar" ? "رمز التحقق (2FA)" : "2FA Code"}
                  </Label>
                  <Input id="otp" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="123456"
                    data-testid="login-otp" inputMode="numeric" />
                </div>
                <Button type="submit" size="lg" className="w-full gap-2 rounded-xl bg-emerald-600 font-bold shadow-lg shadow-emerald-600/25 hover:bg-emerald-700"
                  disabled={loading} data-testid="login-otp-submit">
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("confirm")}
                </Button>
              </form>
            )}

            <p className="mt-6 text-center text-sm text-slate-600">
              {lang === "ar" ? "طالب جديد؟" : "New student?"}{" "}
              <Link to="/signup" className="font-bold text-emerald-700 hover:underline" data-testid="login-go-signup">
                {lang === "ar" ? "أنشئ حساب" : "Create account"}
              </Link>
            </p>
          </div>

          <p className="mt-6 text-center text-xs text-slate-400">
            © 2026/2027 · {t("school_short")}
          </p>
        </div>
      </div>
    </div>
  );
}
