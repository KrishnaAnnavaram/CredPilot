/* CredPilot web client.
 *
 * One page, no framework. It streams Server-Sent Events from the backend so a
 * fifteen-second assessment shows which agent is working rather than spinning,
 * and it renders exactly what the API returns. It computes nothing: every
 * figure, citation and outcome on this page came out of the graph.
 */

const $ = (id) => document.getElementById(id);

const state = {
  threadId: null,
  awaitingClarification: false,
  product: "mortgage",
  applications: { mortgage: [], education: [] },
  busy: false,
};

/* ----------------------------------------------------------------- utilities */

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

/** Escape, then apply the small subset of Markdown the backend emits.
 *  Escaping first is what makes this safe: no path here can produce a tag that
 *  did not come from this function. */
function renderMarkdown(text) {
  const escaped = String(text ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return escaped
    .split(/\n{2,}/)
    .map((block) => {
      const trimmed = block.trim();
      if (!trimmed) return "";
      if (trimmed.startsWith("&gt; ")) {
        return `<blockquote>${inline(trimmed.replace(/^&gt; ?/gm, ""))}</blockquote>`;
      }
      return `<p>${inline(trimmed).replace(/\n/g, "<br>")}</p>`;
    })
    .join("");
}

function inline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function money(value) {
  return `$${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

function ratio(value) {
  return `${(Number(value) * 100).toFixed(2)}%`;
}

/* ---------------------------------------------------------------- transcript */

function addMessage(role, html, extraClass) {
  const wrap = el("div", `message ${role}${extraClass ? " " + extraClass : ""}`);
  const bubble = el("div", "bubble");
  bubble.innerHTML = html;
  wrap.appendChild(bubble);
  $("transcript").appendChild(wrap);
  $("transcript").scrollTop = $("transcript").scrollHeight;
  return wrap;
}

function addThinking(label) {
  const wrap = el("div", "message assistant thinking");
  const bubble = el("div", "bubble");
  bubble.appendChild(el("span", "spinner"));
  bubble.appendChild(el("span", "", label));
  wrap.appendChild(bubble);
  $("transcript").appendChild(wrap);
  $("transcript").scrollTop = $("transcript").scrollHeight;
  return wrap;
}

/* ------------------------------------------------------------------ progress */

function resetRun() {
  $("progress").innerHTML = "";
  $("m-route").textContent = "—";
  $("m-domain").textContent = "—";
  $("m-status").textContent = "working…";
  $("m-elapsed").textContent = "—";
  $("decision-panel").hidden = true;
  $("evidence-panel").hidden = true;
}

function markNode(node, label) {
  const list = $("progress");
  [...list.children].forEach((li) => li.classList.remove("active"));
  const item = el("li", "done active", label);
  item.dataset.node = node;
  list.appendChild(item);
}

/* -------------------------------------------------------------------- result */

function renderResult(result) {
  state.threadId = result.thread_id;

  $("m-route").textContent = result.route || "—";
  $("m-domain").textContent = result.loan_domain
    ? result.loan_domain.replace("_", " ").toLowerCase()
    : "—";
  $("m-elapsed").textContent = `${result.elapsed_seconds}s`;
  [...$("progress").children].forEach((li) => li.classList.remove("active"));

  if (result.awaiting_clarification) {
    state.awaitingClarification = true;
    $("m-status").textContent = "awaiting your answer";
    $("clarify").hidden = false;
    $("clarify-question").innerHTML = inline(
      String(result.clarification?.question ?? "")
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    );
    $("hint").textContent = "Answering the question above resumes the same thread.";
    if (result.answer) addMessage("assistant", renderMarkdown(result.answer));
    renderDebug(result);
    return;
  }

  state.awaitingClarification = false;
  $("clarify").hidden = true;
  $("hint").textContent = "Enter to send · Shift+Enter for a new line";
  $("m-status").textContent = result.requires_human_review ? "human review" : "done";

  if (result.answer) addMessage("assistant", renderMarkdown(result.answer));

  renderDecision(result);
  renderCitations(result);
  renderDebug(result);
}

function renderDecision(result) {
  // `{}` is truthy in JavaScript, and a policy answer carries an empty figures
  // object — so testing `result.figures?.ratios` showed an empty Recommendation
  // panel on every question. Test for content, not for presence.
  const hasFigures = Object.keys(result.figures?.ratios ?? {}).length > 0;
  if (!result.outcome && !hasFigures) {
    $("decision-panel").hidden = true;
    return;
  }
  $("decision-panel").hidden = false;

  const outcome = result.outcome || "—";
  const tone = outcome.startsWith("APPROVE") ? "approve"
    : outcome.startsWith("DECLINE") ? "decline"
    : outcome.startsWith("REFER") ? "refer" : "";
  const node = $("d-outcome");
  node.textContent = outcome.replace(/_/g, " ");
  node.className = `outcome ${tone}`;

  const review = $("d-review");
  review.hidden = !result.requires_human_review;
  review.textContent = "A human must review this before any decision is communicated.";

  const reasons = $("d-reasons");
  reasons.innerHTML = "";
  (result.human_review_reasons || []).slice(0, 6).forEach((reason) =>
    reasons.appendChild(el("li", "", reason))
  );

  const figures = $("d-figures");
  figures.innerHTML = "";
  const ratios = result.figures?.ratios || {};
  Object.keys(ratios).sort().forEach((name) => {
    const row = figures.insertRow();
    row.insertCell().textContent = name.replace(/_/g, " ");
    row.insertCell().textContent = ratio(ratios[name]);
  });
  (result.figures?.indeterminate || []).forEach((name) => {
    const row = figures.insertRow();
    row.className = "indeterminate";
    row.insertCell().textContent = String(name).replace(/_/g, " ");
    row.insertCell().textContent = "indeterminate";
  });

  const breaches = $("d-breaches");
  breaches.innerHTML = "";
  (result.breaches || []).forEach((breach) => {
    const div = el("div", "breach");
    div.innerHTML =
      `<strong>${String(breach.measure).replace(/_/g, " ")}</strong> — ` +
      `observed <span class="mono">${Number(breach.observed).toFixed(4)}</span> ` +
      `${String(breach.comparator ?? "")} ` +
      `<span class="mono">${Number(breach.threshold).toFixed(4)}</span><br>` +
      `<span class="mono">${String(breach.citation ?? "")}</span>`;
    breaches.appendChild(div);
  });
}

function renderCitations(result) {
  const citations = result.citations || [];
  $("evidence-panel").hidden = citations.length === 0;
  $("e-count").textContent = citations.length
    ? `${citations.length} distinct · ${result.evidence_count} chunks`
    : "";
  const list = $("citations");
  list.innerHTML = "";
  citations.forEach((citation) => list.appendChild(el("li", "", citation)));
}

function renderDebug(result) {
  $("x-thread").textContent = result.thread_id || "—";
  $("x-intent").textContent = result.intent || "—";
  $("x-decidedby").textContent = result.decided_by || "—";
  $("x-confidence").textContent =
    result.confidence == null ? "—" : Number(result.confidence).toFixed(2);
  $("x-steps").textContent = `${result.steps_taken} of ${result.step_budget}`;
  $("x-narrative").textContent = result.narrative_model
    ? `${result.narrative_model} · ${result.narrative_faithful ? "grounded" : "unsupported claim"}`
    : "no model call";

  const guard = result.output_guardrail || {};
  $("x-guardrails").textContent = [
    guard.pii_redacted ? "PII redacted" : "no PII found",
    ...(result.security_findings?.length
      ? [`input: ${result.security_findings.join(", ")}`] : []),
    ...(guard.notices?.length ? guard.notices : []),
  ].join(" · ") || "clean";

  $("x-agents").textContent = (result.agents_executed || []).join(" → ") || "—";

  const retrieval = [];
  if (result.policy_questions?.length)
    retrieval.push(`${result.policy_questions.length} topic question(s)`);
  if (result.required_rules_fetched?.length)
    retrieval.push(`${result.required_rules_fetched.length} rule(s) fetched by id`);
  if (result.policy_dependencies?.length)
    retrieval.push(`${result.policy_dependencies.length} dependency follow(s)`);
  if (result.degradations?.length)
    retrieval.push(`${result.degradations.length} tool failure(s)`);
  $("x-retrieval").textContent = retrieval.join(" · ") ||
    (result.retrieval_invoked ? "invoked" : "not invoked");

  const validation = result.validation || {};
  $("x-validation").textContent =
    validation.passed === undefined ? "—"
      : validation.passed ? "passed: citations resolve, figures supported, decision consistent"
      : (validation.failures || []).join("; ");
}

/* ------------------------------------------------------------------ streaming */

async function stream(url, body) {
  if (state.busy) return;
  state.busy = true;
  $("send").disabled = true;
  resetRun();

  const thinking = addThinking("Working…");

  let response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (error) {
    thinking.remove();
    addMessage("assistant", `<p>Could not reach the server: ${error}</p>`, "error");
    finish();
    return;
  }

  if (!response.ok) {
    thinking.remove();
    let detail = `${response.status}`;
    try { detail = (await response.json()).detail ?? detail; } catch { /* body is not JSON */ }
    addMessage("assistant", `<p>${detail}</p>`, "error");
    finish();
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      const line = frame.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      let event;
      try { event = JSON.parse(line.slice(6)); } catch { continue; }

      if (event.event === "node") {
        markNode(event.node, event.label);
        thinking.querySelector(".bubble span:last-child").textContent = event.label + "…";
      } else if (event.event === "result") {
        thinking.remove();
        renderResult(event);
      } else if (event.event === "error") {
        thinking.remove();
        addMessage(
          "assistant",
          `<p><strong>${event.error_type}</strong> — ${event.message}</p>`,
          "error"
        );
        $("m-status").textContent = "error";
      }
    }
  }
  finish();
}

function finish() {
  state.busy = false;
  $("send").disabled = false;
  $("input").focus();
}

/* -------------------------------------------------------------------- actions */

function send() {
  const input = $("input");
  const message = input.value.trim();
  if (!message || state.busy) return;

  addMessage("user", renderMarkdown(message));
  input.value = "";
  input.style.height = "auto";

  if (state.awaitingClarification && state.threadId) {
    stream("/api/chat/resume", { thread_id: state.threadId, answer: message });
  } else {
    stream("/api/chat", { message, thread_id: state.threadId });
  }
}

function assess(applicationId) {
  if (state.busy) return;
  // A fresh thread per application: resuming an assessment thread with a second
  // application would replay the first one's checkpoint.
  state.threadId = null;
  state.awaitingClarification = false;
  addMessage("user", `<p>Assess application <code>${applicationId}</code></p>`);
  stream("/api/assess", { application_id: applicationId });
}

/* ------------------------------------------------------------------ bootstrap */

async function loadHealth() {
  try {
    const health = await (await fetch("/api/health")).json();
    const dot = $("status-dot");
    const parts = [];
    if (health.indexes?.built) {
      parts.push("indexes built");
      dot.className = "dot ok";
    } else {
      parts.push("indexes missing — run build_policy_indexes.py");
      dot.className = "dot bad";
    }
    if (health.model?.available) {
      parts.push(health.model.model);
    } else {
      parts.push("no model key — deterministic summaries");
      if (dot.className === "dot ok") dot.className = "dot warn";
    }
    $("status-text").textContent = parts.join(" · ");
  } catch {
    $("status-dot").className = "dot bad";
    $("status-text").textContent = "backend unreachable";
  }
}

async function loadApplications() {
  try {
    const data = await (await fetch("/api/applications?limit=12")).json();
    state.applications = data.products || {};
    renderApplications();
  } catch {
    $("applications").innerHTML = "<li class='muted'>could not load</li>";
  }
}

function renderApplications() {
  const list = $("applications");
  list.innerHTML = "";
  const rows = state.applications[state.product] || [];
  if (!rows.length) {
    list.appendChild(el("li", "muted", "none found"));
    return;
  }
  rows.forEach((row) => {
    const item = el("li");
    const button = el("button");
    button.innerHTML =
      `<span class="aid">${row.application_id}</span>` +
      `<span class="asum">${row.summary} · ${row.as_of_date ?? ""}</span>`;
    button.addEventListener("click", () => assess(row.application_id));
    item.appendChild(button);
    list.appendChild(item);
  });
}

function bind() {
  $("composer").addEventListener("submit", (event) => {
    event.preventDefault();
    send();
  });

  const input = $("input");
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  });
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
  });

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      state.product = tab.dataset.product;
      renderApplications();
    });
  });

  const toggle = $("debug-toggle");
  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!open));
    $("debug").hidden = open;
  });
}

bind();
loadHealth();
loadApplications();
$("input").focus();
