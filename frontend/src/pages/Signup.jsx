import React, { useEffect, useState } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import { School, Loader2, KeyRound, User, Mail, Lock, IdCard, Sparkles, ArrowLeft } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useLang } from "@/lib/i18n";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Signup() {
  const { t, lang, toggle } = useLang();
  const { user, setUser, loadMe } = useAuth();
  const navigate = useNavigate();
  const [info, setInfo] = useState(null);
  const [form, setForm] = useState({
    school_key: "", full_name: "", email: "", password: "", student_number: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/auth/school-info").then(({ data }) => setInfo(data)).catch(() => setInfo({}));
  }, []);

  if (user && user.id) return <Navigate to="/dashboard" replace />;

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const payload = { ...form };
      if (!payload.student_number) delete payload.student_number;
      await api.post("/auth/signup/student", payload);
      await loadMe();
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(apiError(err, lang === "ar" ? "تعذّر إنشاء الحساب" : "Sign up failed"));
    } finally {
      setLoading(false);
    }
  };

  const disabled = info && info.signup_enabled === false;

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
        <div className="w-full max-w-xl">
          {/* Top nav */}
          <div className="mb-6 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 text-sm font-bold text-slate-700 hover:text-emerald-700">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-lg shadow-emerald-600/25">
                <School className="h-5 w-5" />
              </div>
              <span className="hidden sm:inline">{t("app_name")}</span>
            </Link>
            <button onClick={toggle} className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-bold text-slate-700 hover:bg-slate-100" data-testid="signup-lang-toggle">
              {lang === "ar" ? "English" : "العربية"}
            </button>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-2xl shadow-slate-900/10 backdrop-blur-xl sm:p-10">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">
              <Sparkles className="h-3.5 w-3.5" /> {lang === "ar" ? "حساب طالب جديد" : "New student account"}
            </span>
            <h1 className="mt-4 text-2xl font-extrabold text-slate-900 sm:text-3xl">
              {lang === "ar" ? "أنشئ حسابك الآن" : "Create your account"}
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              {info?.school_name_ar || t("school_short")}
            </p>

            {disabled && (
              <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800">
                {lang === "ar" ? "تسجيل الطلاب معطّل حاليًا. تواصل مع إدارة المدرسة." : "Student signup is disabled. Please contact your school."}
              </div>
            )}

            {error && (
              <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700" data-testid="signup-error">
                {error}
              </div>
            )}

            <form onSubmit={submit} className="mt-6 space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="school_key" className="flex items-center gap-2 text-slate-700">
                  <KeyRound className="h-4 w-4 text-emerald-600" />
                  {lang === "ar" ? "مفتاح المدرسة" : "School key"}
                </Label>
                <Input
                  id="school_key" required value={form.school_key}
                  onChange={(e) => set("school_key", e.target.value.toUpperCase())}
                  placeholder="XXXX-XXXX-XXXX-XXXX"
                  className="font-mono tracking-wider"
                  data-testid="signup-school-key"
                  autoComplete="off"
                />
                <p className="text-xs text-slate-500">
                  {lang === "ar" ? "اطلب المفتاح من مدير المدرسة" : "Ask your school director for the key"}
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label htmlFor="full_name" className="flex items-center gap-2 text-slate-700">
                    <User className="h-4 w-4 text-emerald-600" />
                    {lang === "ar" ? "الاسم الكامل" : "Full name"}
                  </Label>
                  <Input id="full_name" required value={form.full_name} onChange={(e) => set("full_name", e.target.value)}
                    placeholder={lang === "ar" ? "اسمك الرباعي" : "Your full name"} data-testid="signup-full-name" />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="student_number" className="flex items-center gap-2 text-slate-700">
                    <IdCard className="h-4 w-4 text-emerald-600" />
                    {lang === "ar" ? "رقم الطالب (اختياري)" : "Student number (optional)"}
                  </Label>
                  <Input id="student_number" value={form.student_number} onChange={(e) => set("student_number", e.target.value)}
                    placeholder="e.g. 2026001" data-testid="signup-student-number" />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="email" className="flex items-center gap-2 text-slate-700">
                  <Mail className="h-4 w-4 text-emerald-600" />
                  {t("email")}
                </Label>
                <Input id="email" type="email" required value={form.email} onChange={(e) => set("email", e.target.value)}
                  placeholder="name@school.edu" data-testid="signup-email" autoComplete="email" />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="password" className="flex items-center gap-2 text-slate-700">
                  <Lock className="h-4 w-4 text-emerald-600" />
                  {t("password")}
                </Label>
                <Input id="password" type="password" required minLength={6} value={form.password}
                  onChange={(e) => set("password", e.target.value)} placeholder="••••••••"
                  data-testid="signup-password" autoComplete="new-password" />
                <p className="text-xs text-slate-500">
                  {lang === "ar" ? "٦ أحرف على الأقل" : "At least 6 characters"}
                </p>
              </div>

              <Button type="submit" size="lg" className="w-full gap-2 rounded-xl bg-emerald-600 font-bold shadow-lg shadow-emerald-600/25 hover:bg-emerald-700"
                disabled={loading || disabled} data-testid="signup-submit">
                {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> {lang === "ar" ? "جارٍ الإنشاء..." : "Creating..."}</>
                  : <>{lang === "ar" ? "إنشاء الحساب" : "Create account"} <ArrowLeft className={lang === "ar" ? "h-5 w-5" : "h-5 w-5 rotate-180"} /></>}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-slate-600">
              {lang === "ar" ? "لديك حساب بالفعل؟" : "Already have an account?"}{" "}
              <Link to="/login" className="font-bold text-emerald-700 hover:underline" data-testid="signup-go-login">
                {t("login")}
              </Link>
            </p>
          </div>

          <p className="mt-6 text-center text-xs text-slate-400">
            © 2026 · {info?.school_name_ar || t("school_short")}
          </p>
        </div>
      </div>
    </div>
  );
}
