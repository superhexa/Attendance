import React, { useState } from "react";
import { useNavigate, useLocation, Navigate } from "react-router-dom";
import { School, Loader2, ShieldCheck } from "lucide-react";
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
      setError(apiError(err, "تعذّر تسجيل الدخول"));
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
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Visual side */}
      <div className="relative hidden overflow-hidden bg-slate-900 lg:block">
        <img
          src="https://images.pexels.com/photos/5147366/pexels-photo-5147366.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
          alt="school"
          className="absolute inset-0 h-full w-full object-cover opacity-40"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/70 to-slate-900/30" />
        <div className="relative flex h-full flex-col justify-between p-12 text-white">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500 text-slate-900">
              <School className="h-7 w-7" />
            </div>
            <span className="text-lg font-bold">{t("app_name")}</span>
          </div>
          <div className="space-y-4">
            <h2 className="text-4xl font-extrabold leading-tight">
              مدرسة الملك حسين بن طلال الثانوية الشاملة للبنين
            </h2>
            <p className="max-w-md text-lg text-slate-300">
              منصة متكاملة لإدارة الحضور المدرسي — دقيقة، آمنة، وسريعة.
            </p>
            <div className="flex items-center gap-2 text-sm text-emerald-400">
              <ShieldCheck className="h-4 w-4" /> نظام محمي بصلاحيات دقيقة وسجل تدقيق كامل
            </div>
          </div>
          <p className="text-sm text-slate-500">© 2026/2027</p>
        </div>
      </div>

      {/* Form side */}
      <div className="flex items-center justify-center bg-background p-6">
        <div className="w-full max-w-sm animate-fade-up">
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-2 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                <School className="h-6 w-6" />
              </div>
              <span className="font-bold">{t("app_name")}</span>
            </div>
            <button onClick={toggle} className="ms-auto rounded-lg border px-3 py-1.5 text-sm font-bold hover:bg-muted" data-testid="login-lang-toggle">
              {lang === "ar" ? "English" : "العربية"}
            </button>
          </div>

          <h1 className="text-3xl font-extrabold text-foreground">{t("login")}</h1>
          <p className="mb-8 mt-1 text-sm text-muted-foreground">{t("login_subtitle")}</p>

          {error && (
            <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-400" data-testid="login-error">
              {error}
            </div>
          )}

          {!twofa ? (
            <form onSubmit={submit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="email">{t("email")}</Label>
                <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@school.edu" data-testid="login-email" autoComplete="email" />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">{t("password")}</Label>
                <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••" data-testid="login-password" autoComplete="current-password" />
              </div>
              <label className="flex items-center gap-2 text-sm text-muted-foreground">
                <Checkbox checked={remember} onCheckedChange={(v) => setRemember(!!v)} data-testid="login-remember" />
                {t("remember_me")}
              </label>
              <Button type="submit" className="w-full font-bold" size="lg" disabled={loading} data-testid="login-submit">
                {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> {t("signing_in")}</> : t("login")}
              </Button>
            </form>
          ) : (
            <form onSubmit={submitOtp} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="otp">رمز التحقق (2FA)</Label>
                <Input id="otp" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="123456"
                  data-testid="login-otp" inputMode="numeric" />
              </div>
              <Button type="submit" className="w-full font-bold" size="lg" disabled={loading} data-testid="login-otp-submit">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : t("confirm")}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
