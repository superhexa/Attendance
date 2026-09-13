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
      <section className="relative overflow-hidden pt-32 pb-20 sm:pt-40 lg:pb-28">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-24 start-1/4 h-96 w-96 rounded-full bg-emerald-200/50 blur-3xl" />
          <div className="absolute top-20 end-0 h-80 w-80 rounded-full bg-amber-200/40 blur-3xl" />
          <div className="absolute inset-0" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, rgba(15,76,58,0.06) 1px, transparent 0)", backgroundSize: "28px 28px" }} />
        </div>

        <div className="relative mx-auto grid max-w-7xl items-center gap-14 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <div className="animate-fade-up">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-sm font-bold text-emerald-700">
              <Sparkles className="h-4 w-4" /> منصة إدارة حضور احترافية
            </span>
            <h1 className="mt-6 text-4xl font-extrabold leading-tight text-slate-900 sm:text-5xl lg:text-6xl">
              حضور المدرسة،
              <span className="bg-gradient-to-l from-emerald-600 to-teal-500 bg-clip-text text-transparent"> بدقّة وسرعة</span>
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-slate-600">
              نظام متكامل لمدرسة الملك حسين بن طلال الثانوية الشاملة للبنين — تسجيل حضور فوري، صلاحيات دقيقة، تقارير وتحليلات، وإشعارات لحظية. كل ذلك بواجهة عربية أنيقة.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link to={target}>
                <Button size="lg" className="gap-2 rounded-xl bg-emerald-600 px-7 text-base font-bold shadow-lg shadow-emerald-600/25 hover:bg-emerald-700" data-testid="landing-cta-login">
                  ابدأ الآن <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <a href="#features">
                <Button size="lg" variant="outline" className="rounded-xl border-slate-300 px-7 text-base font-bold text-slate-700 hover:bg-slate-50" data-testid="landing-explore">
                  استكشف المميزات
                </Button>
              </a>
            </div>
            <div className="mt-10 grid max-w-md grid-cols-3 gap-6">
              {[["٨", "أدوار وصلاحيات"], ["٥", "حالات حضور"], ["100%", "على الخادم آمن"]].map(([n, l]) => (
                <div key={l}>
                  <p className="text-2xl font-extrabold text-emerald-700">{n}</p>
                  <p className="text-xs font-medium text-slate-500">{l}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Hero visual */}
          <div className="relative animate-fade-up" style={{ animationDelay: "0.15s" }}>
            <div className="relative overflow-hidden rounded-3xl border border-slate-200 shadow-2xl shadow-slate-900/10">
              <img
                src="https://images.pexels.com/photos/5147366/pexels-photo-5147366.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                alt="school" className="h-[420px] w-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-emerald-950/50 to-transparent" />
            </div>
            {/* Floating card - rate */}
            <div className="absolute -start-4 top-10 w-44 rounded-2xl border border-slate-100 bg-white/95 p-4 shadow-xl backdrop-blur">
              <p className="text-xs font-medium text-slate-500">نسبة الحضور اليوم</p>
              <p className="mt-1 text-3xl font-extrabold text-emerald-600">94%</p>
              <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100">
                <div className="h-1.5 w-[94%] rounded-full bg-emerald-500" />
              </div>
            </div>
            {/* Floating card - attendance row */}
            <div className="absolute -end-4 bottom-8 w-52 rounded-2xl border border-slate-100 bg-white/95 p-3 shadow-xl backdrop-blur">
              <p className="mb-2 text-xs font-bold text-slate-700">الرياضيات · شعبة أ</p>
              {[["عمر خليل", true], ["حمزة فيصل", true], ["يوسف أحمد", false]].map(([nm, present]) => (
                <div key={nm} className="flex items-center justify-between py-1 text-xs">
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
      <section id="features" className="bg-slate-50 py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-bold uppercase tracking-wide text-emerald-600">المميزات</p>
            <h2 className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">كل ما تحتاجه مدرستك في مكان واحد</h2>
            <p className="mt-4 text-lg text-slate-600">أدوات مصمّمة لتوفير الوقت وضمان دقة بيانات الحضور.</p>
          </div>
          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f, i) => (
              <div key={f.title} className="group rounded-2xl border border-slate-200 bg-white p-7 shadow-sm transition-all hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg animate-fade-up" style={{ animationDelay: `${i * 0.05}s` }}>
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
      <section id="roles" className="py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-bold uppercase tracking-wide text-emerald-600">لوحة لكل مستخدم</p>
            <h2 className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">تجربة مصمّمة لكل دور</h2>
          </div>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {ROLES.map((r) => (
              <div key={r.title} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
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
      <section id="how" className="bg-slate-50 py-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm font-bold uppercase tracking-wide text-emerald-600">كيف يعمل</p>
            <h2 className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">ثلاث خطوات فقط</h2>
          </div>
          <div className="mt-14 grid gap-8 md:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.n} className="relative rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-600 text-2xl font-extrabold text-white">{s.n}</div>
                <h3 className="mt-5 text-lg font-bold text-slate-900">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-l from-emerald-700 to-teal-600 px-8 py-14 text-center shadow-2xl shadow-emerald-700/20">
            <div className="pointer-events-none absolute -top-16 end-10 h-56 w-56 rounded-full bg-white/10 blur-2xl" />
            <h2 className="relative text-3xl font-extrabold text-white sm:text-4xl">جاهز لبدء إدارة الحضور بذكاء؟</h2>
            <p className="relative mx-auto mt-4 max-w-xl text-emerald-50">سجّل الدخول بحساب المدرسة وابدأ خلال دقائق.</p>
            <Link to={target} className="relative mt-8 inline-block">
              <Button size="lg" className="gap-2 rounded-xl bg-white px-8 text-base font-bold text-emerald-700 hover:bg-emerald-50" data-testid="landing-bottom-cta">
                تسجيل الدخول <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
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
