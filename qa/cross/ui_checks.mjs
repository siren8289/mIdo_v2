#!/usr/bin/env node
// security_scan.py와 코드를 공유하지 않는 화면·설정 검사.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = import.meta.dirname ?? dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");

function read(rel) {
  const text = readFileSync(join(root, rel), "utf8");
  return { text, lines: text.split(/\n/) };
}

function lineOf(lines, needle) {
  const index = lines.findIndex((line) => line.includes(needle));
  return index === -1 ? "UNKNOWN" : String(index + 1);
}

function fnOf(lines, lineNo) {
  if (lineNo === "UNKNOWN") return "UNKNOWN";
  for (let i = Number(lineNo) - 1; i >= 0; i -= 1) {
    const stripped = lines[i].trim();
    if (stripped.includes("function ")) {
      return stripped.split("function ")[1].split("(")[0].trim();
    }
  }
  return "UNKNOWN";
}

function item(id, status, rel, lines, needle, expected, actual, evidence, cause = "", input = "") {
  const line = needle ? lineOf(lines, needle) : "UNKNOWN";
  return {
    id, status, expected, actual, evidence,
    file: rel,
    function: fnOf(lines, line),
    line,
    input,
    error: status === "FAIL" ? actual : "",
    cause,
  };
}

function walk(dir, acc = []) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) walk(path, acc);
    else acc.push(path);
  }
  return acc;
}

const cases = [];
const result = read("front/src/pages/ResultPage.tsx");
const hrefBad = result.text.includes("href={item.source_url}")
  && !result.text.includes('startsWith("https')
  && !result.text.includes("protocol");
cases.push(item(
  "SEC-HREF", hrefBad ? "FAIL" : "PASS",
  "front/src/pages/ResultPage.tsx", result.lines, "href={item.source_url}",
  "https 등 허용 스킴만 링크",
  hrefBad ? "스킴 검사 없이 href에 source_url" : "스킴 검사 있음",
  "node가 ResultPage를 읽음",
  hrefBad ? "javascript: URL이 href로 들어갈 수 있다." : "",
  "source_url=javascript:alert(1)",
));

let levelStatus = "ERROR";
let levelActual = "LEVEL 블록을 실행하지 못함";
let levelCause = "";
try {
  const start = result.text.indexOf("const LEVEL");
  const end = result.text.indexOf("};", start);
  let block = result.text.slice(start, end + 2);
  const colon = block.indexOf(":");
  const eq = block.indexOf("=");
  if (colon === -1 || eq === -1 || colon > eq) throw new Error("LEVEL 선언을 나누지 못함");
  block = `${block.slice(0, colon)} ${block.slice(eq)}`;
  const fn = new Function(`${block}; const result = { level: "unknown" }; return (LEVEL[result.level] ?? LEVEL.none).label;`);
  levelActual = fn();
  const sourceHasFallback = result.text.includes("LEVEL[result.level] ?? LEVEL.none");
  levelStatus = sourceHasFallback && levelActual === "문제 없음" ? "FAIL" : "PASS";
  if (levelStatus === "FAIL") levelCause = "unknown level 실행 결과가 문제 없음이다.";
} catch (error) {
  levelStatus = "ERROR";
  levelActual = String(error);
  levelCause = "node 실행 실패";
}
cases.push(item(
  "SEC-LEVEL", levelStatus,
  "front/src/pages/ResultPage.tsx", result.lines, "LEVEL[result.level] ?? LEVEL.none",
  "unknown level 라벨은 문제 없음이 아님",
  levelActual,
  "타입 주석을 지운 LEVEL 객체를 node Function으로 실행",
  levelCause,
  "level=unknown",
));

const keyBad = result.text.includes("key={item.vuln_id}");
cases.push(item(
  "SEC-REACT-KEY", keyBad ? "FAIL" : "PASS",
  "front/src/pages/ResultPage.tsx", result.lines, "key={item.vuln_id}",
  "중복 vuln_id여도 키가 유일",
  keyBad ? "key가 vuln_id뿐" : "유일 키",
  "node가 key 속성을 읽음",
  keyBad ? "같은 vuln_id면 React 키가 같다." : "",
));

const app = read("front/src/App.tsx");
const no404 = !app.text.includes('path="*"') && !app.text.includes("path='*'");
cases.push(item(
  "SEC-NO-404", no404 ? "FAIL" : "PASS",
  "front/src/App.tsx", app.lines, "<Routes>",
  "path=* 라우트",
  no404 ? "path=* 없음" : "catch-all 있음",
  "node가 App.tsx를 읽음",
  no404 ? "없는 URL용 화면이 없다." : "",
  "/no-such-page",
));

let danger = null;
for (const path of walk(join(root, "front/src"))) {
  if (!/\.(tsx|ts|jsx|js)$/.test(path)) continue;
  const text = readFileSync(path, "utf8");
  if (text.includes("dangerouslySetInnerHTML")) {
    danger = path.slice(root.length + 1);
    break;
  }
}
cases.push(item(
  "SEC-NO-DANGEROUS", danger ? "FAIL" : "PASS",
  danger || "front/src",
  ["// scan"],
  danger ? "dangerouslySetInnerHTML" : "",
  "dangerouslySetInnerHTML 0건",
  danger ? `사용 ${danger}` : "0건",
  "node가 front/src를 읽음",
  danger ? "HTML 삽입 API가 있다." : "",
));

const nginx = read("front/nginx.conf");
const tlsBad = nginx.text.includes("listen 80") && !nginx.text.includes("listen 443");
cases.push(item(
  "SEC-TLS", tlsBad ? "FAIL" : "PASS",
  "front/nginx.conf", nginx.lines, "listen 80",
  "443 리스너",
  tlsBad ? "80만 있음" : "443 있음",
  "node가 nginx.conf를 읽음",
  tlsBad ? "평문 HTTP만 리스닝한다." : "",
));

const deploy = read(".github/workflows/deploy.yml");
const checkoutBad = deploy.text.includes("actions/checkout@v4") && !deploy.text.includes("workflow_run.head_sha");
cases.push(item(
  "SEC-CHECKOUT", checkoutBad ? "FAIL" : "PASS",
  ".github/workflows/deploy.yml", deploy.lines, "actions/checkout@v4",
  "checkout ref가 workflow_run.head_sha",
  checkoutBad ? "head_sha ref 없음" : "head_sha 있음",
  "node가 deploy.yml을 읽음",
  checkoutBad ? "검사한 커밋이 아닌 기본 브랜치를 받을 수 있다." : "",
));

const handler = read("back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java");
const generic = handler.text.includes('서버 오류가 발생했습니다.');
cases.push(item(
  "SEC-GENERIC-500", generic ? "PASS" : "FAIL",
  "back/src/main/java/com/mido/global/exception/GlobalExceptionHandler.java",
  handler.lines, "서버 오류가 발생했습니다.",
  "미처리 예외 본문은 고정 문장",
  generic ? "고정 문장 있음" : "고정 문장 없음",
  "node가 GlobalExceptionHandler를 읽음",
  generic ? "" : "예외 내용이 본문에 나갈 수 있다.",
));

process.stdout.write(JSON.stringify({ tool: "ui_checks", cases }));
