let currentTicketId = null;

function getToken() {
    return localStorage.getItem("access_token");
}

function setToken(token) {
    if (token) {
        localStorage.setItem("access_token", token);
    } else {
        localStorage.removeItem("access_token");
    }
}

async function api(path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
    };

    const token = getToken();

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(path, {
        headers,
        ...options,
    });

    if (response.status === 401) {
        setToken(null);
        showMessage("Sessão expirada ou não autenticada.", "error");
        showView("login");
        throw new Error("Não autenticado.");
    }

    if (!response.ok) {
        let detail = `Erro ${response.status}`;

        try {
            const body = await response.json();
            if (body.detail) {
                detail = body.detail;
            }
        } catch {
            // Ignora erro de parse e usa mensagem padrão.
        }

        throw new Error(detail);
    }

    return response.json();
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("nav button").forEach((button) => {
        button.addEventListener("click", () => {
            showView(button.dataset.view);
        });
    });

    document
        .getElementById("reload-dashboard")
        .addEventListener("click", loadDashboard);

    document
        .getElementById("new-ticket-form")
        .addEventListener("submit", createTicket);

    document
        .getElementById("load-tickets-btn")
        .addEventListener("click", loadTickets);

    document
        .getElementById("back-to-tickets")
        .addEventListener("click", () => showView("tickets"));

    document
        .getElementById("login-form")
        .addEventListener("submit", login);

    document
        .getElementById("register-btn")
        .addEventListener("click", registerUser);

    document
        .getElementById("logout-btn")
        .addEventListener("click", logout);

    loadAuthStatus();
    function navigate() {
        const hash = window.location.hash.replace("#", "") || "dashboard";
        if (hash.startsWith("ticket/")) {
            const ticketId = hash.split("/")[1];
            openTicket(ticketId);
        } else {
            showView(hash);
        }
    }
    navigate();
    window.addEventListener("hashchange", navigate);
});

function showView(view) {
    document.querySelectorAll("main section").forEach((section) => {
        section.hidden = true;
    });

    document.querySelectorAll("nav button").forEach((button) => {
        button.classList.remove("active");
    });

    const section = document.getElementById(`view-${view}`);
    if (section) {
        section.hidden = false;
    }

    const navButton = document.querySelector(`nav button[data-view="${view}"]`);
    if (navButton) {
        navButton.classList.add("active");
    }

    if (view === "dashboard") {
        loadDashboard();
    }

    if (view === "tickets") {
        loadTickets();
    }

    if (view === "login") {
        loadAuthStatus();
    }
}

function showMessage(text, type = "success") {
    const message = document.getElementById("message");

    message.textContent = text;
    message.className = `message ${type}`;
    message.hidden = false;

    setTimeout(() => {
        message.hidden = true;
    }, 5000);
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function formatValue(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return value;
}

function formatRate(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value, digits = 2) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toFixed(digits);
}

function card(label, value) {
    return `
        <div class="card">
            <div class="card-label">${escapeHtml(label)}</div>
            <div class="card-value">${escapeHtml(String(value))}</div>
        </div>
    `;
}

function renderKeyValueTable(container, obj) {
    const entries = Object.entries(obj || {});

    if (entries.length === 0) {
        container.innerHTML = "<p>Sem dados.</p>";
        return;
    }

    const rows = entries
        .map(([key, value]) => {
            const safeKey = key === null || key === undefined ? "N/A" : key;

            return `
                <tr>
                    <td>${escapeHtml(safeKey)}</td>
                    <td>${escapeHtml(String(value))}</td>
                </tr>
            `;
        })
        .join("");

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Quantidade</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

async function loadDashboard() {
    try {
        const metrics = await api("/metrics");

        const latency =
            metrics.ai_avg_latency_ms === null ||
            metrics.ai_avg_latency_ms === undefined
                ? "-"
                : Math.round(metrics.ai_avg_latency_ms);

        document.getElementById("metric-cards").innerHTML = [
            card("Chamados", formatValue(metrics.tickets_total)),
            card("Sugestões da IA", formatValue(metrics.ai_suggestions_total)),
            card("Revisões", formatValue(metrics.ai_reviews_total)),
            card("Aceitas", formatRate(metrics.ai_accepted_rate)),
            card("Corrigidas", formatRate(metrics.ai_corrected_rate)),
            card("Confiança média", formatNumber(metrics.ai_avg_confidence)),
            card("Latência média (ms)", latency),
            card("Urgência média", formatNumber(metrics.ai_avg_urgency_score)),
        ].join("");

        renderKeyValueTable(
            document.getElementById("tickets-by-status"),
            metrics.tickets_by_status
        );

        renderKeyValueTable(
            document.getElementById("tickets-by-category"),
            metrics.tickets_by_category
        );

        renderKeyValueTable(
            document.getElementById("tickets-by-priority"),
            metrics.tickets_by_priority
        );

        renderKeyValueTable(
            document.getElementById("ai-by-decision"),
            metrics.ai_by_decision
        );
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function createTicket(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const payload = {
        requester_name: formData.get("requester_name"),
        requester_email: formData.get("requester_email"),
        title: formData.get("title"),
        description: formData.get("description"),
        source: formData.get("source") || "portal",
    };

    const category = formData.get("category");
    const priority = formData.get("priority");

    if (category) {
        payload.category = category;
    }

    if (priority) {
        payload.priority = priority;
    }

    try {
        const result = await api("/tickets", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        showMessage(`Chamado #${result.ticket.id} criado com sucesso.`, "success");

        form.reset();

        await openTicket(result.ticket.id);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function loadTickets() {
    const status = document.getElementById("filter-status").value;
    const priority = document.getElementById("filter-priority").value;
    const category = document.getElementById("filter-category").value.trim();

    const params = new URLSearchParams();

    if (status) {
        params.set("status", status);
    }

    if (priority) {
        params.set("priority", priority);
    }

    if (category) {
        params.set("category", category);
    }

    try {
        const tickets = await api(`/tickets?${params.toString()}`);
        renderTicketsTable(tickets);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderTicketsTable(tickets) {
    const container = document.getElementById("tickets-table");

    if (!tickets.length) {
        container.innerHTML = "<p>Nenhum chamado encontrado.</p>";
        return;
    }

    const rows = tickets
        .map((ticket) => {
            return `
                <tr>
                    <td>${escapeHtml(ticket.id)}</td>
                    <td>${escapeHtml(ticket.title)}</td>
                    <td>${escapeHtml(ticket.category || "-")}</td>
                    <td>${escapeHtml(ticket.priority)}</td>
                    <td>${escapeHtml(ticket.status)}</td>
                    <td>${ticket.needs_review ? "Sim" : "Não"}</td>
                    <td>
                        <button type="button" onclick="openTicket(${ticket.id})">
                            Detalhes
                        </button>
                    </td>
                </tr>
            `;
        })
        .join("");

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Título</th>
                    <th>Categoria</th>
                    <th>Prioridade</th>
                    <th>Status</th>
                    <th>Revisão</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
    `;
}

async function openTicket(ticketId) {
    currentTicketId = ticketId;

    showView("ticket-detail");

    try {
        const ticket = await api(`/tickets/${ticketId}`);
        renderTicketDetail(ticket);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function renderTicketDetail(ticket) {
    const container = document.getElementById("ticket-detail");

    const suggestions = ticket.suggestions || [];

    container.innerHTML = `
        <h2>Chamado #${ticket.id}</h2>

        <div class="detail-grid">
            <div class="detail-item">
                <strong>Título</strong>
                ${escapeHtml(ticket.title)}
            </div>

            <div class="detail-item">
                <strong>Solicitante</strong>
                ${escapeHtml(ticket.requester_name)}
            </div>

            <div class="detail-item">
                <strong>E-mail</strong>
                ${escapeHtml(ticket.requester_email)}
            </div>

            <div class="detail-item">
                <strong>Categoria</strong>
                ${escapeHtml(ticket.category || "-")}
            </div>

            <div class="detail-item">
                <strong>Prioridade</strong>
                ${escapeHtml(ticket.priority)}
            </div>

            <div class="detail-item">
                <strong>Status</strong>
                ${escapeHtml(ticket.status)}
            </div>

            <div class="detail-item">
                <strong>Origem</strong>
                ${escapeHtml(ticket.source)}
            </div>

            <div class="detail-item">
                <strong>Precisa de revisão?</strong>
                ${ticket.needs_review ? "Sim" : "Não"}
            </div>
        </div>

        <div class="detail-item">
            <strong>Descrição</strong>
            <p>${escapeHtml(ticket.description).replaceAll("\n", "<br>")}</p>
        </div>

        <h3>Atualizar status</h3>

        <form id="ticket-status-form" class="form">
            <label>
                Status
                <select name="status">
                    <option value="aberto">Aberto</option>
                    <option value="em_analise">Em análise</option>
                    <option value="aguardando">Aguardando</option>
                    <option value="resolvido">Resolvido</option>
                    <option value="fechado">Fechado</option>
                </select>
            </label>

            <button type="submit">Salvar status</button>
        </form>

        <h3>Sugestões da IA</h3>

        ${
            suggestions.length
                ? suggestions.map(renderSuggestion).join("")
                : "<p>Nenhuma sugestão gerada.</p>"
        }
    `;

    document
        .getElementById("ticket-status-form")
        .addEventListener("submit", updateTicketStatus);

    document.querySelector(
        '#ticket-status-form select[name="status"]'
    ).value = ticket.status;

    suggestions.forEach((suggestion) => {
        const form = document.getElementById(`review-form-${suggestion.id}`);

        if (form) {
            form.addEventListener("submit", (event) => {
                submitReview(event, suggestion.id);
            });
        }
    });
}

function renderSuggestion(suggestion) {
    return `
        <div class="suggestion">
            <p>
                <strong>Provider:</strong> ${escapeHtml(suggestion.provider)} |
                <strong>Confiança:</strong> ${formatNumber(suggestion.confidence)} |
                <strong>Decisão:</strong> ${escapeHtml(suggestion.decision || "-")}
            </p>

            <p>
                <strong>Categoria sugerida:</strong>
                ${escapeHtml(suggestion.suggested_category || "-")}
            </p>

            <p>
                <strong>Prioridade sugerida:</strong>
                ${escapeHtml(suggestion.suggested_priority || "-")}
            </p>

            <p>
                <strong>Resumo:</strong>
                ${escapeHtml(suggestion.summary || "-")}
            </p>

            <p>
                <strong>Ação sugerida:</strong>
                ${escapeHtml(suggestion.suggested_action || "-")}
            </p>

            <form id="review-form-${suggestion.id}" class="review-form">
                <label>
                    Atendente
                    <input
                        type="text"
                        name="reviewer_name"
                        value="Atendente Portfolio"
                        minlength="3"
                        maxlength="120"
                        required
                    >
                </label>

                <label>
                    Decisão da revisão
                    <select name="review_action">
                        <option value="accept">Aceitar sugestão</option>
                        <option value="correct">Corrigir sugestão</option>
                    </select>
                </label>

                <label>
                    Categoria corrigida
                    <input
                        type="text"
                        name="corrected_category"
                        maxlength="80"
                        placeholder="Ex: Infraestrutura"
                    >
                </label>

                <label>
                    Prioridade corrigida
                    <select name="corrected_priority">
                        <option value="">-</option>
                        <option value="baixa">Baixa</option>
                        <option value="media">Média</option>
                        <option value="alta">Alta</option>
                        <option value="critica">Crítica</option>
                    </select>
                </label>

                <label>
                    Observações
                    <textarea
                        name="notes"
                        rows="3"
                        maxlength="1000"
                        placeholder="Explique por que aceitou ou corrigiu a sugestão."
                    ></textarea>
                </label>

                <button type="submit">Salvar revisão</button>
            </form>
        </div>
    `;
}

async function updateTicketStatus(event) {
    event.preventDefault();

    const form = event.target;
    const status = form.elements["status"].value;

    try {
        await api(`/tickets/${currentTicketId}`, {
            method: "PATCH",
            body: JSON.stringify({ status }),
        });

        showMessage("Status atualizado com sucesso.", "success");

        await openTicket(currentTicketId);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function submitReview(event, suggestionId) {
    event.preventDefault();

    const form = event.target;

    const reviewerName = form.elements["reviewer_name"].value;
    const reviewAction = form.elements["review_action"].value;
    const correctedCategory = form.elements["corrected_category"].value.trim();
    const correctedPriority = form.elements["corrected_priority"].value;
    const notes = form.elements["notes"].value.trim();

    const payload = {
        reviewer_name: reviewerName,
        accepted: reviewAction === "accept",
    };

    if (reviewAction === "correct") {
        if (correctedCategory) {
            payload.corrected_category = correctedCategory;
        }

        if (correctedPriority) {
            payload.corrected_priority = correctedPriority;
        }

        if (notes) {
            payload.notes = notes;
        }
    } else if (notes) {
        payload.notes = notes;
    }

    try {
        await api(`/suggestions/${suggestionId}/review`, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        showMessage("Revisão salva com sucesso.", "success");

        await openTicket(currentTicketId);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function login(event) {
    event.preventDefault();

    const form = event.target;

    const payload = {
        email: form.elements["email"].value,
        password: form.elements["password"].value,
    };

    try {
        const data = await api("/auth/token", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        setToken(data.access_token);

        showMessage("Login realizado com sucesso.", "success");

        await loadAuthStatus();

        showView("dashboard");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function registerUser() {
    const form = document.getElementById("login-form");

    const email = form.elements["email"].value;
    const password = form.elements["password"].value;

    if (!email || !password) {
        showMessage("Preencha e-mail e senha para criar a conta.", "error");
        return;
    }

    const payload = {
        name: email.split("@")[0],
        email: email,
        password: password,
        role: "requester",
    };

    try {
        await api("/auth/register", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        showMessage("Conta criada com sucesso! Agora faça login.", "success");
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function logout() {
    setToken(null);

    showMessage("Sessão encerrada.", "success");

    loadAuthStatus();

    showView("login");
}

async function loadAuthStatus() {
    const statusElement = document.getElementById("auth-status");

    if (!statusElement) {
        return;
    }

    try {
        const me = await api("/auth/me");

        statusElement.innerHTML = `
            <p style="margin: 0 0 6px 0;">
                Autenticado como:
                <strong>${escapeHtml(me.name)}</strong>
                (${escapeHtml(me.email)})
            </p>
            <p style="margin: 0;">
                Perfil de acesso:
                <strong>${escapeHtml(me.role)}</strong>
            </p>
        `;
    } catch {
        statusElement.innerHTML = "<p style='margin:0;'>Não autenticado.</p>";
    }
}
