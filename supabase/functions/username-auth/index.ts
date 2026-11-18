import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Content-Type": "application/json",
};

function reply(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), { status, headers: cors });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return reply(405, { error: "지원하지 않는 요청입니다." });
  try {
    const { action, username: rawUsername, password } = await req.json();
    const username = String(rawUsername ?? "").trim().toLowerCase();
    if (!/^[a-z0-9_]{3,20}$/.test(username)) return reply(400, { error: "아이디는 영문 소문자, 숫자, 밑줄(_) 조합 3~20자로 입력하세요." });
    if (typeof password !== "string" || password.length < 8 || password.length > 128) return reply(400, { error: "비밀번호는 8~128자로 입력하세요." });
    if (action !== "signup" && action !== "signin") return reply(400, { error: "잘못된 요청입니다." });

    const url = Deno.env.get("SUPABASE_URL");
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
    if (!url || !serviceKey || !anonKey) {
      console.error("Missing Supabase function environment configuration.");
      return reply(500, { error: "인증 서버 설정을 확인해야 합니다." });
    }
    const admin = createClient(url, serviceKey, { auth: { autoRefreshToken: false, persistSession: false } });
    const publicClient = createClient(url, anonKey, { auth: { autoRefreshToken: false, persistSession: false } });
    const internalEmail = username + "@accounts.aether.invalid";

    if (action === "signup") {
      const { data: created, error: createError } = await admin.auth.admin.createUser({
        email: internalEmail, password, email_confirm: true,
        user_metadata: { username, display_name: username },
      });
      if (createError || !created.user) {
        const message = createError?.message ?? "";
        if (/already|registered|exists|duplicate/i.test(message)) return reply(409, { error: "이미 사용 중인 아이디입니다." });
        console.error("Username signup failed:", message);
        return reply(400, { error: "계정을 만들지 못했습니다. 입력 내용을 확인하세요." });
      }
      const { error: registryError } = await admin.from("username_registry").insert({ username, user_id: created.user.id });
      if (registryError) {
        await admin.auth.admin.deleteUser(created.user.id);
        if (registryError.code === "23505") return reply(409, { error: "이미 사용 중인 아이디입니다." });
        console.error("Username registry insert failed:", registryError.message);
        return reply(500, { error: "계정 정보를 저장하지 못했습니다." });
      }
    } else {
      const { data: account, error: lookupError } = await admin.from("username_registry")
        .select("user_id").eq("username", username).maybeSingle();
      if (lookupError || !account) return reply(401, { error: "아이디 또는 비밀번호가 올바르지 않습니다." });
    }

    const { data: signedIn, error: signInError } = await publicClient.auth.signInWithPassword({ email: internalEmail, password });
    if (signInError || !signedIn.session || !signedIn.user) {
      if (action === "signup") {
        console.error("New account could not start a session:", signInError?.message);
        return reply(500, { error: "계정은 만들어졌지만 로그인하지 못했습니다. 다시 로그인해 주세요." });
      }
      return reply(401, { error: "아이디 또는 비밀번호가 올바르지 않습니다." });
    }
    return reply(200, {
      session: { access_token: signedIn.session.access_token, refresh_token: signedIn.session.refresh_token },
      user: { id: signedIn.user.id, username, user_metadata: { username, display_name: username } },
    });
  } catch (error) {
    console.error("username-auth error:", error);
    return reply(400, { error: "요청을 처리하지 못했습니다. 다시 시도해 주세요." });
  }
});
