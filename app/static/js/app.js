/**
 * HelpDesk IA - Frontend Client Scripts
 */

// Exemplos pré-configurados para testes rápidos
const EXAMPLES = {
  rede: {
    name: "Ana Souza Teste",
    email: "ana.teste@exemplo.com",
    category: "outros",
    title: "Wi-Fi da diretoria caindo e VPN não conecta",
    desc: "Desde as 9h da manhã o Wi-Fi do 3º andar está oscilando, a internet está muito lenta e a VPN corporativa não conecta no notebook."
  },
  seguranca: {
    name: "Bruno Lima Teste",
    email: "bruno.teste@exemplo.com",
    category: "outros",
    title: "E-mail suspeito de banco pedindo senha",
    desc: "Recebi um e-mail com anexo estranho que parece phishing pedindo para atualizar meus acessos bancários urgentemente."
  },
  senha: {
    name: "Carla Mendes Teste",
    email: "carla.teste@exemplo.com",
    category: "outros",
    title: "Conta de usuário bloqueada após errar login",
    desc: "Não consigo entrar no ERP, meu CPF é 123.456.789-09, telefone (11) 98765-4321 e a senha: MinhaSenhaAntiga123 está dando como incorreta."
  }
};

function fillExample(type) {
  const data = EXAMPLES[type];
  if (!data) return;
  document.getElementById('requester_name').value = data.name;
  document.getElementById('requester_email').value = data.email;
  document.getElementById('initial_category').value = data.category;
  document.getElementById('title').value = data.title;
  document.getElementById('description').value = data.desc;
}

async function handleCreateTicket(event) {
  event.preventDefault();
  const form = event.target;
  const feedback = document.getElementById('formFeedback');
  const submitBtn = document.getElementById('submitBtn');

  const payload = {
    requester_name: document.getElementById('requester_name').value.trim(),
    requester_email: document.getElementById('requester_email').value.trim(),
    initial_category: document.getElementById('initial_category').value,
    title: document.getElementById('title').value.trim(),
    description: document.getElementById('description').value.trim(),
    source: "web"
  };

  submitBtn.disabled = true;
  submitBtn.innerText = "⏳ Processando sanitização & IA...";
  feedback.style.display = "none";

  try {
    const res = await fetch('/api/tickets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.ok) {
      feedback.className = "alert alert-success";
      feedback.innerHTML = `✅ Chamado <strong>#${data.id}</strong> criado com sucesso! Redirecionando para a triagem da IA...`;
      feedback.style.display = "block";
      setTimeout(() => {
        window.location.href = `/tickets/${data.id}`;
      }, 1000);
    } else {
      let msg = "Erro ao abrir chamado.";
      if (data.detail && Array.isArray(data.detail)) {
        msg = data.detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join('<br>');
      } else if (data.error && data.error.message) {
        msg = data.error.message;
      }
      feedback.className = "alert alert-danger";
      feedback.innerHTML = `⚠️ ${msg}`;
      feedback.style.display = "block";
      submitBtn.disabled = false;
      submitBtn.innerText = "🚀 Enviar Chamado & Analisar com IA";
    }
  } catch (err) {
    feedback.className = "alert alert-danger";
    feedback.innerHTML = `⚠️ Erro de conexão com o servidor: ${err.message}`;
    feedback.style.display = "block";
    submitBtn.disabled = false;
    submitBtn.innerText = "🚀 Enviar Chamado & Analisar com IA";
  }
}

function toggleReviewMode(mode) {
  const confForm = document.getElementById('confirmForm');
  const chgForm = document.getElementById('changeForm');
  if (mode === 'confirm') {
    confForm.style.display = confForm.style.display === 'none' ? 'block' : 'none';
    chgForm.style.display = 'none';
  } else {
    chgForm.style.display = chgForm.style.display === 'none' ? 'block' : 'none';
    confForm.style.display = 'none';
  }
}

async function handleConfirmReview(event, ticketId) {
  event.preventDefault();
  const reviewer = document.getElementById('conf_reviewer').value.trim();
  const note = document.getElementById('conf_note').value.trim() || null;

  try {
    const res = await fetch(`/api/tickets/${ticketId}/review/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewed_by: reviewer, note: note })
    });

    if (res.ok) {
      window.location.reload();
    } else {
      const err = await res.json();
      alert(`Erro ao confirmar: ${err.error?.message || 'Falha na requisição'}`);
    }
  } catch (e) {
    alert(`Erro de conexão: ${e.message}`);
  }
}

async function handleChangeReview(event, ticketId) {
  event.preventDefault();
  const reviewer = document.getElementById('chg_reviewer').value.trim();
  const category = document.getElementById('chg_category').value;
  const priority = document.getElementById('chg_priority').value;
  const note = document.getElementById('chg_note').value.trim() || null;

  try {
    const res = await fetch(`/api/tickets/${ticketId}/review/change`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reviewed_by: reviewer,
        category: category,
        priority: priority,
        note: note
      })
    });

    if (res.ok) {
      window.location.reload();
    } else {
      const err = await res.json();
      alert(`Erro ao alterar: ${err.error?.message || 'Falha na requisição'}`);
    }
  } catch (e) {
    alert(`Erro de conexão: ${e.message}`);
  }
}

async function updateTicketStatus(ticketId, newStatus) {
  const changedBy = prompt("Informe o nome do atendente que está alterando o status:", "Carlos Atendente Teste");
  if (!changedBy) return;

  try {
    const res = await fetch(`/api/tickets/${ticketId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus, changed_by: changedBy })
    });

    if (res.ok) {
      window.location.reload();
    } else {
      const err = await res.json();
      alert(`Erro ao atualizar status: ${err.error?.message || 'Transição inválida'}`);
    }
  } catch (e) {
    alert(`Erro de conexão: ${e.message}`);
  }
}
