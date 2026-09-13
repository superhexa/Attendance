import React, { useState } from "react";
import { toast } from "sonner";
import { api, apiError } from "@/lib/api";
import { useLang } from "@/lib/i18n";
import { PageHeader } from "@/components/PageHeader";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { QrCode, CheckCircle2, Loader2 } from "lucide-react";

export default function ScanQR() {
  const { t } = useLang();
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/attendance/qr/scan", { code });
      setDone(true); toast.success("تم تسجيل حضورك");
    } catch (err) { toast.error(apiError(err)); } finally { setLoading(false); }
  };
  return (
    <div>
      <PageHeader title={t("nav.qr_scan")} subtitle="أدخل رمز الحضور الذي عرضه المعلم" breadcrumb={t("group_main")} />
      <Card className="mx-auto max-w-md">
        <CardContent className="flex flex-col items-center gap-5 p-8 text-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            {done ? <CheckCircle2 className="h-10 w-10 text-emerald-600" /> : <QrCode className="h-10 w-10" />}
          </div>
          {done ? (
            <p className="text-lg font-bold text-emerald-600">تم تسجيل حضورك بنجاح</p>
          ) : (
            <form onSubmit={submit} className="w-full space-y-4">
              <Input placeholder="رمز الحضور" value={code} onChange={(e) => setCode(e.target.value)} required
                className="text-center text-lg font-bold" data-testid="qr-code-input" />
              <Button type="submit" className="w-full font-bold" size="lg" disabled={loading} data-testid="qr-submit">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "تأكيد الحضور"}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
