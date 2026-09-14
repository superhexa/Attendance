import React from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  School, ClipboardCheck, ShieldCheck, BarChart3, Bell, QrCode, ScrollText,
  CalendarDays, Users2, GraduationCap, ArrowLeft, Check, Sparkles, LayoutDashboard,
} from "lucide-react";
import { useLang } from "@/lib/i18n";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";

const FEATURES = [
  { icon: ClipboardCheck, title: "تسجيل حضور فائق السرعة", desc: "سجّل حضور الشعبة بالكامل بنقرة واحدة؛ الجميع حاضر افتراضيًا وتُعدَّل الاستثناءات فقط في ثوانٍ." },
  { icon: ShieldCheck, title: "صلاحيات دقيقة (RBAC)", desc: "ثمانية أدوار مع صلاحيات قابلة للتخصيص لكل مستخدم ونطاق وصول محدود لكل معلم." },
  { icon: BarChart3, title: "تقارير وتحليلات فورية", desc: "لوحات ورسوم بيانية حيّة، اتجاهات الحضور، ومقارنة الشعب مع تصدير CSV وفلاتر متقدمة." },
  { icon: Bell, title: "إشعارات لحظية", desc: "تنبيهات الغياب المتكرر ومركز إشعارات داخلي متكامل للمدراء والمعلمين والطلاب." },
  { icon: QrCode, title: "حضور عبر رمز QR", desc: "رمز مؤقت يُنشئه المعلم ويمسحه الطلاب لتسجيل حضور آمن لا يقبل التكرار أو التزوير." },
  { icon: ScrollText, title: "أمان وسجل تدقيق", desc: "سجل تدقيق غير قابل للتعديل، إدارة الجلسات، ومصادقة ثنائية اختيارية للمشرفين." },
];

const ROLES = [
  { icon: LayoutDashboard, title: "المدير", color: "from-emerald-500 to-teal-600", points: ["نظرة شاملة على المدرسة", "مؤشرات ورسوم بيانية", "إدارة كاملة للصلاحيات"] },
  { icon: Users2, title: "المعلم", color: "from-amber-500 to-orange-600", points: ["حصص اليوم بلمسة واحدة", "تسجيل حضور سريع", "متابعة الغياب المتكرر"] },
  { icon: GraduationCap, title: "الطالب", color: "from-sky-500 to-indigo-600", points: ["نسبة الحضور والسجل", "جدول اليوم", "الإعلانات والإشعارات"] },
];

const STEPS = [
  { n: "١", title: "أنشئ الهيكل الدراسي", desc: "أعوام دراسية، صفوف، وشعب في دقائق." },
  { n: "٢", title: "أسند المعلمين والجداول", desc: "مع كشف تلقائي لتعارض الحصص." },
  { n: "٣", title: "سجّل الحضور واحصل على التقارير", desc: "تحليلات وتنبيهات فورية." },
];

function Nav() {
  const { toggle, lang } = useLang();
  const { user } = useAuth();
  const target = user?.id ? "/dashboard" : "/login";
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white shadow-lg shadow-emerald-600/20">
            <School className="h-6 w-6" />
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-extrabold leading-tight text-slate-900">نظام الحضور المدرسي</p>
            <p className="text-[11px] text-slate-500">مدرسة الملك حسين بن طلال</p>
          </div>
        </div>
        <nav className="hidden items-center gap-8 text-sm font-semibold text-slate-600 md:flex">
          <a href="#features" className="transition-colors hover:text-emerald-700">المميزات</a>
          <a href="#roles" className="transition-colors hover:text-emerald-700">الأدوار</a>
          <a href="#how" className="transition-colors hover:text-emerald-700">كيف يعمل</a>
        </nav>
        <div className="flex items-center gap-2">
          <button onClick={toggle} className="rounded-lg px-2.5 py-1.5 text-sm font-bold text-slate-600 hover:bg-slate-100" data-testid="landing-lang-toggle">
            {lang === "ar" ? "EN" : "ع"}
          </button>
          {!user?.id && (
            <Link to="/signup" className="hidden sm:inline-block">
              <Button variant="outline" className="rounded-lg border-slate-300 font-bold text-slate-700 hover:bg-slate-50" data-testid="landing-nav-signup">
                {lang === "ar" ? "تسجيل طالب" : "Sign up"}
              </Button>
            </Link>
          )}
          <Link to={target}>
            <Button className="gap-2 rounded-lg bg-emerald-600 font-bold hover:bg-emerald-700" data-testid="landing-nav-login">
              {user?.id ? "لوحة التحكم" : "تسجيل الدخول"}
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Landing() {
  const { user } = useAuth();
  const target = user?.id ? "/dashboard" : "/login";

  return (
    <div className="min-h-screen bg-white text-slate-900" dir="rtl">
      <Nav />

      {/* Hero */}
      <section className="relative overflow-hidden pt-28 pb-16 sm:pt-32 sm:pb-20 lg:pt-40 lg:pb-24">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-24 start-1/4 h-72 w-72 rounded-full bg-emerald-200/50 blur-3xl sm:h-96 sm:w-96" />
          <div className="absolute top-20 end-0 h-64 w-64 rounded-full bg-amber-200/40 blur-3xl sm:h-80 sm:w-80" />
          <div className="absolute inset-0" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, rgba(15,76,58,0.06) 1px, transparent 0)", backgroundSize: "28px 28px" }} />
        </div>

        <div className="relative mx-auto grid max-w-7xl items-center gap-10 px-4 sm:px-6 md:gap-14 lg:grid-cols-2 lg:px-8">
          <div className="animate-fade-up text-center lg:text-start">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-xs font-bold text-emerald-700 sm:text-sm">
              <Sparkles className="h-4 w-4" /> منصة إدارة حضور احترافية
            </span>
            <h1 className="mt-5 text-3xl font-extrabold leading-tight text-slate-900 sm:text-5xl lg:text-6xl">
              حضور المدرسة،
              <span className="bg-gradient-to-l from-emerald-600 to-teal-500 bg-clip-text text-transparent"> بدقّة وسرعة</span>
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg lg:mx-0">
              نظام متكامل لمدرسة الملك حسين بن طلال الثانوية الشاملة للبنين — تسجيل حضور فوري، صلاحيات دقيقة، تقارير وتحليلات، وإشعارات لحظية.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3 lg:justify-start">
              <Link to={target}>
                <Button size="lg" className="gap-2 rounded-xl bg-emerald-600 px-6 text-base font-bold shadow-lg shadow-emerald-600/25 hover:bg-emerald-700 sm:px-7" data-testid="landing-cta-login">
                  ابدأ الآن <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <a href="#features">
                <Button size="lg" variant="outline" className="rounded-xl border-slate-300 px-6 text-base font-bold text-slate-700 hover:bg-slate-50 sm:px-7" data-testid="landing-explore">
                  استكشف المميزات
                </Button>
              </a>
            </div>
          </div>

          {/* Hero visual */}
          <div className="relative mx-auto w-full max-w-md animate-fade-up lg:max-w-none" style={{ animationDelay: "0.15s" }}>
            <div className="relative overflow-hidden rounded-3xl border border-slate-200 shadow-2xl shadow-slate-900/10">
              <img
                src="https://images.pexels.com/photos/5147366/pexels-photo-5147366.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                alt="school" className="h-64 w-full object-cover sm:h-80 lg:h-[420px]"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-emerald-950/50 to-transparent" />
            </div>
            {/* Floating card - rate */}
            <div className="absolute -start-2 top-6 w-36 rounded-2xl border border-slate-100 bg-white/95 p-3 shadow-xl backdrop-blur sm:-start-4 sm:top-10 sm:w-44 sm:p-4">
              <p className="text-[10px] font-medium text-slate-500 sm:text-xs">نسبة الحضور اليوم</p>
              <p className="mt-1 text-2xl font-extrabold text-emerald-600 sm:text-3xl">94%</p>
              <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100">
                <div className="h-1.5 w-[94%] rounded-full bg-emerald-500" />
              </div>
            </div>
            {/* Floating card - attendance row */}
            <div className="absolute -end-2 bottom-6 w-44 rounded-2xl border border-slate-100 bg-white/95 p-3 shadow-xl backdrop-blur sm:-end-4 sm:bottom-8 sm:w-52">
              <p className="mb-2 text-[11px] font-bold text-slate-700 sm:text-xs">الرياضيات · شعبة أ</p>
              {[["عمر خليل", true], ["حمزة فيصل", true], ["يوسف أحمد", false]].map(([nm, present]) => (
                <div key={nm} className="flex items-center justify-between py-1 text-[11px] sm:text-xs">
                  <span className="text-slate-600">{nm}</span>
                  <span className={`flex h-5 w-5 items-center justify-center rounded-full ${present ? "bg-emerald-100 text-emerald-600" : "bg-rose-100 text-rose-600"}`}>
                    {present ? <Check className="h-3 w-3" /> : "✕"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-slate-50 py-16 sm:py-20 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-600 sm:text-sm">المميزات</p>
            <h2 className="mt-2 text-2xl font-extrabold text-slate-900 sm:text-3xl lg:text-4xl">كل ما تحتاجه مدرستك في مكان واحد</h2>
            <p className="mt-4 text-base text-slate-600 sm:text-lg">أدوات مصمّمة لتوفير الوقت وضمان دقة بيانات الحضور.</p>
          </div>
          <div className="mt-10 grid gap-5 sm:mt-14 sm:grid-cols-2 sm:gap-6 lg:grid-cols-3">
            {FEATURES.map((f, i) => (
              <div key={f.title} className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg animate-fade-up sm:p-7" style={{ animationDelay: `${i * 0.05}s` }}>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-600/10 text-emerald-600 transition-colors group-hover:bg-emerald-600 group-hover:text-white">
                  <f.icon className="h-6 w-6" />
                </div>
                <h3 className="mt-5 text-lg font-bold text-slate-900">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Roles */}
      <section id="roles" className="py-16 sm:py-20 lg:py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-600 sm:text-sm">لوحة لكل مستخدم</p>
            <h2 className="mt-2 text-2xl font-extrabold text-slate-900 sm:text-3xl lg:text-4xl">تجربة مصمّمة لكل دور</h2>
          </div>
          <div className="mt-10 grid gap-5 sm:mt-14 sm:grid-cols-2 sm:gap-6 md:grid-cols-3">
            {ROLES.map((r) => (
              <div key={r.title} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
                <div className={`bg-gradient-to-l ${r.color} p-6 text-white`}>
                  <r.icon className="h-8 w-8" />
                  <h3 className="mt-3 text-xl font-extrabold">{r.title}</h3>
                </div>
                <ul className="space-y-3 p-6">
                  {r.points.map((p) => (
                    <li key={p} className="flex items-center gap-2 text-sm text-slate-700">
                      <Check className="h-4 w-4 shrink-0 text-emerald-600" /> {p}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="bg-slate-50 py-16 sm:py-20 lg:py-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-600 sm:text-sm">كيف يعمل</p>
            <h2 className="mt-2 text-2xl font-extrabold text-slate-900 sm:text-3xl lg:text-4xl">ثلاث خطوات فقط</h2>
          </div>
          <div className="mt-10 grid gap-6 sm:mt-14 sm:grid-cols-2 sm:gap-8 md:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.n} className="relative rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm sm:p-8">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-600 text-2xl font-extrabold text-white">{s.n}</div>
                <h3 className="mt-5 text-lg font-bold text-slate-900">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-14 sm:py-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-l from-emerald-700 to-teal-600 px-6 py-10 text-center shadow-2xl shadow-emerald-700/20 sm:px-8 sm:py-14">
            <div className="pointer-events-none absolute -top-16 end-10 h-56 w-56 rounded-full bg-white/10 blur-2xl" />
            <h2 className="relative text-2xl font-extrabold text-white sm:text-3xl lg:text-4xl">جاهز لبدء إدارة الحضور بذكاء؟</h2>
            <p className="relative mx-auto mt-4 max-w-xl text-sm text-emerald-50 sm:text-base">سجّل الدخول بحساب المدرسة وابدأ خلال دقائق.</p>
            <Link to={target} className="relative mt-8 inline-block">
              <Button size="lg" className="gap-2 rounded-xl bg-white px-7 text-base font-bold text-emerald-700 hover:bg-emerald-50 sm:px-8" data-testid="landing-bottom-cta">
                تسجيل الدخول <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-8 sm:py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 text-center sm:flex-row sm:px-6 sm:text-start lg:px-8">
          <div className="flex flex-col items-center gap-3 sm:flex-row">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-white"><School className="h-5 w-5" /></div>
            <div>
              <p className="text-sm font-bold text-slate-900">مدرسة الملك حسين بن طلال الثانوية الشاملة للبنين</p>
              <p className="text-xs text-slate-500">نظام إدارة الحضور المدرسي · 2026/2027</p>
            </div>
          </div>
          <p className="text-xs text-slate-400">© 2026 جميع الحقوق محفوظة</p>
        </div>
      </footer>
    </div>
  );
}
