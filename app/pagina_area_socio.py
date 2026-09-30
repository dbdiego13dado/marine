from app.configurazione import CONFIGURAZIONE_APP, PERCORSO_BASE, configurazione_frontend_json


def pagina_area_socio() -> str:
    pagina = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>__TITOLO_AREA_SOCIO__</title>
      <style>
        :root {
          --sfondo: #f3efe4;
          --sfondo-secondario: #f7f3ea;
          --card: rgba(255, 255, 255, 0.92);
          --testo: #14363a;
          --testo-chiaro: #476a6f;
          --bordo: #cfe0db;
          --accento: #177f97;
          --accento-scuro: #11647a;
          --verde: #1f6f5f;
          --verde-scuro: #164d42;
          --chiaro: #ecf4f1;
          --occupata: #fff1ef;
          --occupata-bordo: #efb2ab;
          --libera: #ecfbf5;
          --libera-bordo: #8bd2aa;
          --errore: #b42318;
          --successo: #0f7b44;
          --ombra: 0 18px 40px rgba(20, 54, 58, 0.10);
        }
        * { box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
          margin: 0;
          font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
          color: var(--testo);
          background:
            radial-gradient(circle at top left, rgba(23, 127, 151, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(31, 111, 95, 0.10), transparent 24%),
            linear-gradient(180deg, #faf7f0 0%, var(--sfondo) 42%, #edf4ef 100%);
        }
        .pagina { max-width: 1180px; margin: 0 auto; padding: 22px 18px 60px; }
        .sito-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          padding: 14px 0 24px;
          flex-wrap: wrap;
        }
        .logo-titolo {
          color: var(--accento);
          font-weight: 900;
          letter-spacing: 0.02em;
          line-height: 0.92;
          text-decoration: none;
          display: inline-block;
        }
        .logo-titolo .logo-immagine {
          display: block;
          width: min(520px, 78vw);
          height: auto;
        }
        .logo-titolo .grande { display: block; font-size: 48px; }
        .logo-titolo .medio { display: block; font-size: 31px; }
        .logo-titolo .vela {
          display: block;
          font-size: 20px;
          letter-spacing: 0.34em;
          color: #58a9c0;
          margin-top: 6px;
        }
        .menu-principale {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          align-items: center;
        }
        .voce-menu {
          border: none;
          background: transparent;
          color: var(--testo);
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          padding: 12px 16px;
          border-radius: 999px;
          transition: background 0.2s ease, color 0.2s ease;
        }
        .voce-menu:hover, .voce-menu.attiva {
          background: rgba(23, 127, 151, 0.10);
          color: var(--accento-scuro);
        }
        .hero {
          display: grid;
          grid-template-columns: minmax(0, 1.12fr) minmax(340px, 0.88fr);
          gap: 26px;
          align-items: stretch;
          margin-bottom: 26px;
        }
        .hero-testo {
          min-height: 420px;
          padding: 34px 36px;
          border-radius: 34px;
          background:
            linear-gradient(130deg, rgba(255,255,255,0.84), rgba(255,255,255,0.70)),
            radial-gradient(circle at top right, rgba(23, 127, 151, 0.18), transparent 30%),
            radial-gradient(circle at bottom left, rgba(31, 111, 95, 0.12), transparent 30%);
          box-shadow: var(--ombra);
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          border: 1px solid rgba(207, 224, 219, 0.9);
        }
        .eyebrow {
          font-size: 14px;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          color: var(--accento);
          font-weight: 800;
        }
        h1 {
          margin: 12px 0 10px;
          font-size: clamp(42px, 7vw, 72px);
          line-height: 0.95;
          color: var(--testo);
        }
        .sottotitolo {
          max-width: 560px;
          font-size: 20px;
          line-height: 1.45;
          color: var(--testo-chiaro);
          margin: 0 0 16px;
        }
        .testo-hero {
          max-width: 580px;
          font-size: 17px;
          line-height: 1.7;
          color: var(--testo);
        }
        .azioni-hero {
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
          margin-top: 24px;
        }
        button {
          border: none;
          border-radius: 16px;
          padding: 14px 18px;
          font-size: 15px;
          font-weight: 800;
          cursor: pointer;
          transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
        }
        button:hover { transform: translateY(-1px); }
        button:disabled {
          opacity: 0.55;
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
        .primario {
          background: var(--verde);
          color: white;
          box-shadow: 0 12px 22px rgba(31, 111, 95, 0.18);
        }
        .primario:hover { background: var(--verde-scuro); }
        .secondario {
          background: #eef5f3;
          color: var(--testo);
          border: 1px solid rgba(207, 224, 219, 0.9);
        }
        .accento {
          background: var(--accento);
          color: white;
          box-shadow: 0 12px 22px rgba(23, 127, 151, 0.18);
        }
        .accento:hover { background: var(--accento-scuro); }
        .scheda {
          background: var(--card);
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 28px;
          padding: 26px;
          box-shadow: var(--ombra);
          backdrop-filter: blur(8px);
          margin-bottom: 20px;
        }
        .scheda h2, .scheda h3 {
          margin-top: 0;
          margin-bottom: 10px;
          font-size: 32px;
        }
        .scheda p { margin: 0; line-height: 1.65; color: var(--testo-chiaro); }
        .scheda-home { display: flex; flex-direction: column; gap: 20px; }
        .titolo-sezione { font-size: 30px; margin-bottom: 8px; }
        .griglia-due, .griglia-tre {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 14px;
        }
        .campo { margin-bottom: 14px; }
        label { display: block; font-weight: 700; margin-bottom: 8px; }
        input, textarea, select {
          width: 100%;
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 14px;
          padding: 13px 14px;
          font-size: 15px;
          background: rgba(252, 254, 253, 0.95);
          color: var(--testo);
        }
        textarea { min-height: 100px; resize: vertical; }
        .nascosto { display: none !important; }
        .messaggio {
          margin-top: 14px;
          padding: 14px 16px;
          border-radius: 14px;
          font-weight: 700;
          display: none;
        }
        .messaggio.successo {
          display: block;
          background: #ebfff3;
          color: var(--successo);
          border: 1px solid #8bd2aa;
        }
        .messaggio.errore {
          display: block;
          background: #fff2f0;
          color: var(--errore);
          border: 1px solid #efb2ab;
        }
        .orari-home {
          background: rgba(255, 255, 255, 0.82);
          border: 1px solid rgba(207, 224, 219, 0.92);
          border-radius: 24px;
          padding: 22px;
        }
        .orari-home h3 { margin-top: 0; margin-bottom: 12px; font-size: 22px; }
        .griglia-orari {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 14px;
        }
        .scheda-orario {
          background: white;
          border: 1px solid rgba(207, 224, 219, 0.92);
          border-radius: 18px;
          padding: 16px;
          line-height: 1.7;
        }
        .scheda-orario strong { display: block; margin-bottom: 6px; font-size: 18px; }
        .blocco-dashboard {
          display: grid;
          grid-template-columns: minmax(0, 1fr);
          gap: 18px;
        }
        .titolo-benvenuto {
          font-size: 18px;
          color: var(--accento);
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }
        .box-info {
          font-size: clamp(28px, 4vw, 42px);
          font-weight: 900;
          line-height: 1.05;
          background: linear-gradient(180deg, #ffffff, #f4fbf8);
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 20px;
          padding: 20px;
        }
        .azioni { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 18px; }
        .tipologie {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          margin-top: 10px;
        }
        .tipologia-btn {
          background: #eaf3f1;
          border: 1px solid rgba(207, 224, 219, 0.95);
          color: var(--testo);
        }
        .tipologia-btn.attiva {
          background: var(--verde);
          color: white;
        }
        .griglia-barche {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
          gap: 14px;
          margin-top: 14px;
        }
        .griglia-categorie {
          display: grid;
          gap: 18px;
          margin-top: 16px;
        }
        .categoria-imbarcazioni {
          background: rgba(255, 255, 255, 0.82);
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 22px;
          padding: 18px;
        }
        .categoria-imbarcazioni h4 {
          margin: 0 0 6px;
          font-size: 22px;
        }
        .barca {
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 20px;
          padding: 18px;
          cursor: pointer;
          background: #f8fcfa;
        }
        .barca.libera {
          background: var(--libera);
          border-color: var(--libera-bordo);
        }
        .barca.occupata {
          background: var(--occupata);
          border-color: var(--occupata-bordo);
        }
        .barca.selezionata { outline: 3px solid var(--verde); }
        .stato {
          display: inline-block;
          padding: 4px 10px;
          border-radius: 999px;
          font-size: 13px;
          font-weight: 800;
          margin-top: 6px;
        }
        .stato.libera { background: #dbf6e8; color: #0f7b44; }
        .stato.occupata { background: #ffdeda; color: #b42318; }
        .riepilogo-orari {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 14px;
          margin: 14px 0;
        }
        .orario-letto {
          background: #f8fcfa;
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 16px;
          padding: 14px;
        }
        .orario-letto strong { display: block; margin-bottom: 6px; }
        .uscite, .registro {
          display: grid;
          gap: 12px;
          margin-top: 14px;
        }
        .uscita, .riga-registro, .contatto-box {
          background: rgba(255, 255, 255, 0.88);
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 18px;
          padding: 16px;
        }
        .stato-registro {
          display: inline-block;
          margin-top: 8px;
          padding: 4px 10px;
          border-radius: 999px;
          font-size: 13px;
          font-weight: 800;
          background: #e9f2ee;
        }
        .contatti-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 14px;
          margin-top: 14px;
        }
        .titolo-chiudibile {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
        }
        .chiudi-sezione {
          background: #eef5f3;
          color: var(--testo);
          border: 1px solid rgba(207, 224, 219, 0.95);
          border-radius: 12px;
          padding: 8px 14px;
          font-size: 18px;
          line-height: 1;
          min-width: 44px;
        }
        .contatto-box strong { display: block; margin-bottom: 6px; font-size: 17px; }
        .contatto-box a {
          color: var(--accento-scuro);
          font-weight: 700;
          text-decoration: none;
        }
        .elenco-foto {
          margin-top: 8px;
          font-size: 14px;
          color: var(--testo-chiaro);
        }
        @media (max-width: 980px) {
          .hero { grid-template-columns: 1fr; }
          .hero-testo { min-height: auto; }
        }
        @media (max-width: 640px) {
          .pagina { padding: 16px 14px 40px; }
          .logo-titolo .grande { font-size: 40px; }
          .logo-titolo .medio { font-size: 26px; }
          .menu-principale { width: 100%; }
          .voce-menu { width: 100%; text-align: left; }
          .scheda, .hero-testo { padding: 22px; border-radius: 24px; }
          .griglia-orari { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .scheda-orario { padding: 14px; font-size: 14px; }
          .scheda-orario strong { font-size: 16px; }
        }
      </style>
    </head>
    <body>
      <div class="pagina">
        <header class="sito-header">
          <a href="/" class="logo-titolo">
            __LOGO_APP__
          </a>
          <nav class="menu-principale">
            <button class="voce-menu" id="nav-registrati" type="button">Registrati</button>
            <button class="voce-menu" id="nav-modifica-dati" type="button">Modifica dati</button>
            <button class="voce-menu" id="nav-contatti" type="button">Contatti</button>
            <button class="voce-menu" id="nav-amministratore" type="button">Amministratore</button>
          </nav>
        </header>

        <section class="hero">
          <div class="hero-testo">
            <div>
              <div class="eyebrow">__HOME_EYEBROW__</div>
              <h1>__HOME_TITOLO__</h1>
              <p class="sottotitolo">__HOME_SOTTOTITOLO__</p>
              <div class="testo-hero">
                __HOME_TESTO__
              </div>
            </div>
          </div>

          <div class="scheda scheda-home" id="login-socio">
            <div>
              <h2 class="titolo-sezione">Accesso rapido</h2>
              <p>Registra questo telefono una sola volta, oppure collega un profilo gia esistente per accedere direttamente alle prenotazioni.</p>
            </div>
            <div class="azioni" style="margin-top:0;">
              <button class="primario" id="vai-registrazione" type="button">Registra questo telefono</button>
              <button class="secondario" id="mostra-recupero" type="button">Collega un profilo esistente</button>
            </div>
            <div class="orari-home">
              <h3>__ORARI_TITOLO__</h3>
              <div class="griglia-orari">
                <div class="scheda-orario">
                  <strong>__ORARI_SEDE_TITOLO__</strong>
                  __ORARI_FERIALI__<br><br>
                  __ORARI_FESTIVI__
                </div>
                <div class="scheda-orario">
                  <strong>__ORARI_SERVIZIO_TITOLO__</strong>
                  __ORARI_FERIALI__<br><br>
                  __ORARI_FESTIVI__
                </div>
              </div>
            </div>
            <div id="recupero-accesso" class="nascosto">
              <div class="campo">
                <label for="accesso-email">Email</label>
                <input id="accesso-email" type="email">
              </div>
              <div class="campo">
                <label for="accesso-tessera">__ETICHETTA_TESSERA__</label>
                <input id="accesso-tessera">
              </div>
              <div class="azioni">
                <button class="primario" id="entra-socio" type="button">Collega questo telefono</button>
              </div>
            </div>
            <div id="messaggio-accesso" class="messaggio"></div>
          </div>
        </section>

        <section class="scheda nascosto" id="dashboard-socio">
          <div class="blocco-dashboard">
            <div class="titolo-benvenuto" id="titolo-socio"></div>
            <div class="box-info" id="info-socio"></div>
            <div class="azioni" style="margin-top:0;">
              <button class="accento" id="dashboard-prenotazioni" type="button">Prenotazioni imbarcazioni</button>
              <button class="secondario" id="dashboard-registro" type="button">Registro uscite</button>
              <button class="secondario" id="dashboard-regolamento" type="button">Regolamento</button>
            </div>
            <div id="avviso-idoneita" class="messaggio"></div>
            <div id="avviso-notifiche" class="messaggio"></div>
          </div>
          <div id="profilo-socio" class="nascosto">
            <div class="griglia-due">
              <div class="campo">
                <label for="profilo-nome">Nome</label>
                <input id="profilo-nome">
              </div>
              <div class="campo">
                <label for="profilo-cognome">Cognome</label>
                <input id="profilo-cognome">
              </div>
              <div class="campo">
                <label for="profilo-telefono">Telefono</label>
                <input id="profilo-telefono">
              </div>
              <div class="campo">
                <label for="profilo-ruolo">Ruolo</label>
                <select id="profilo-ruolo">
                  <option value="istruttore">Istruttore</option>
                  <option value="abilitato">Abilitato</option>
                  <option value="allievo">Allievo</option>
                </select>
              </div>
            </div>
            <div class="messaggio" style="display:block;">
              Quota annuale e certificato medico possono essere sbloccati solo dall'amministratore.
            </div>
            <div class="azioni">
              <button class="secondario" id="salva-profilo" type="button">Salva modifica</button>
            </div>
          </div>
          <div id="messaggio-azione" class="messaggio"></div>
        </section>

        <section class="scheda" id="prenotazioni-imbarcazioni">
          <h2>Prenotazioni imbarcazioni</h2>
          <p>Seleziona la tipologia, apri la barca che ti interessa e registra l'uscita.</p>
          <div class="campo">
            <label>Tipologia</label>
            <div id="lista-tipologie" class="tipologie"></div>
          </div>
          <div id="elenco-barche" class="griglia-barche"></div>
        </section>

        <section class="scheda">
          <h3>Uscite aperte al circolo</h3>
          <p>Qui i soci vedono le uscite attive del momento e possono aprire direttamente la lista delle barche disponibili.</p>
          <div id="lista-uscite" class="uscite"></div>
        </section>

        <section class="scheda nascosto" id="scheda-imbarcazioni-categorie">
          <h3>Tutte le imbarcazioni</h3>
          <p>Elenco completo delle barche del circolo, divise per categoria.</p>
          <div id="lista-imbarcazioni-categorie" class="griglia-categorie"></div>
        </section>

        <section class="scheda nascosto" id="dettaglio-barca">
          <h2 id="titolo-barca">Imbarcazione</h2>
          <div id="stato-barca"></div>
          <div class="campo">
            <label>Data uscita</label>
            <input id="data-prenotazione" type="date">
          </div>
          <div class="campo">
            <label for="equipaggio-barca">Equipaggio</label>
            <textarea id="equipaggio-barca" placeholder="Scrivi i nomi dell'equipaggio separati da virgola o andando a capo."></textarea>
          </div>
          <div id="riepilogo-occupazione" class="riepilogo-orari nascosto">
            <div class="orario-letto">
              <strong>Ora di partenza</strong>
              <span id="orario-partenza-attivo">-</span>
            </div>
            <div class="orario-letto">
              <strong>Ora di arrivo</strong>
              <span id="orario-arrivo-attivo">-</span>
            </div>
          </div>
          <div id="form-prenotazione">
            <div class="campo">
              <label for="nota-prenotazione">Note</label>
              <textarea id="nota-prenotazione" placeholder="Scrivi per esempio: chi interessato mi contatti in privato."></textarea>
            </div>
            <div class="azioni">
              <button class="primario" id="conferma-prenotazione" type="button">Conferma prenotazione</button>
            </div>
          </div>
          <div id="form-rientro" class="nascosto">
            <div class="griglia-due">
              <div class="campo">
                <label for="chiusura-ora-partenza">Ora di partenza</label>
                <input id="chiusura-ora-partenza" type="time">
              </div>
              <div class="campo">
                <label for="chiusura-ora-rientro">Ora di arrivo</label>
                <input id="chiusura-ora-rientro" type="time">
              </div>
            </div>
            <div class="campo">
              <label for="nota-rientro">Nota finale</label>
              <textarea id="nota-rientro" placeholder="Scrivi che l'imbarcazione e a posto oppure una nota finale."></textarea>
            </div>
            <div class="campo">
              <label for="danni-rientro">Eventuali danni</label>
              <textarea id="danni-rientro" placeholder="Indica eventuali danni o lascia vuoto."></textarea>
            </div>
            <div class="campo">
              <label for="foto-danni">Foto eventuali danni</label>
              <input id="foto-danni-galleria" type="file" accept="image/*" multiple class="nascosto">
              <input id="foto-danni-fotocamera" type="file" accept="image/*" capture="environment" class="nascosto">
              <div class="azioni" style="margin-top:0;">
                <button class="secondario" id="apri-galleria" type="button">Apri galleria</button>
                <button class="secondario" id="apri-fotocamera" type="button">Usa fotocamera</button>
              </div>
              <div id="foto-danni-selezionate" class="elenco-foto">Nessuna foto selezionata.</div>
            </div>
            <div class="azioni">
              <button class="primario" id="chiudi-prenotazione" type="button">Conferma rientro</button>
            </div>
          </div>
        </section>

        <section class="scheda nascosto" id="scheda-registro-uscite">
          <div class="titolo-chiudibile">
            <h3>Registro uscite</h3>
            <button class="chiudi-sezione" id="chiudi-registro-uscite" type="button">X</button>
          </div>
          <p>Storico completo di tutte le uscite registrate, con barca, socio, orari effettivi e note finali.</p>
          <div class="campo">
            <label>Tipologia</label>
            <div id="lista-tipologie-registro" class="tipologie"></div>
          </div>
          <div id="lista-registro-uscite" class="registro"></div>
        </section>

        <section class="scheda" id="contatti-sezione">
          <h3>Contatti</h3>
          <p>__CONTATTI_DESCRIZIONE__</p>
          <div class="contatti-grid">
            <div class="contatto-box">
              <strong>__CONTATTI_TELEFONO_TITOLO__</strong>
              __CONTATTI_TELEFONO_LABEL__<br>
              <a href="tel:__CONTATTI_TELEFONO__">__CONTATTI_TELEFONO_VISIBILE__</a>
            </div>
            <div class="contatto-box">
              <strong>Email ufficiale</strong>
              <a href="mailto:__CONTATTI_EMAIL__">__CONTATTI_EMAIL__</a>
            </div>
            <div class="contatto-box">
              <strong>Location</strong>
              __CONTATTI_LUOGO__<br>
              __CONTATTI_CITTA__
            </div>
          </div>
        </section>
      </div>

        <script>
          const CONFIG_APP = __CONFIGURAZIONE_APP__;
          const CHIAVE_SOCIO = CONFIG_APP.chiave_socio;
          const CHIAVE_USCITE_NOTIFICATE = CONFIG_APP.chiave_uscite_notificate;
          const TIPOLOGIE = CONFIG_APP.tipologie;
          const ETICHETTE_TIPOLOGIE = CONFIG_APP.etichette_tipologie;
          let socioCorrente = null;
          let tipologiaCorrente = TIPOLOGIE[0] || "derive";
          let tipologiaRegistroCorrente = TIPOLOGIE[0] || "derive";
          let barcheCorrenti = [];
          let registroUsciteCorrente = [];
          let barcaSelezionata = null;
          let fotoDanniSelezionate = [];
          let notificheUsciteInizializzate = false;
          let idsUsciteNotificate = new Set();

          const messaggioAccesso = document.getElementById("messaggio-accesso");
          const messaggioAzione = document.getElementById("messaggio-azione");
          const sezionePrenotazioni = document.getElementById("prenotazioni-imbarcazioni");
          const sezioneRegistro = document.getElementById("scheda-registro-uscite");
          const sezioneImbarcazioniCategorie = document.getElementById("scheda-imbarcazioni-categorie");
          const sezioneContatti = document.getElementById("contatti-sezione");

        function collegaClick(id, handler) {
          const elemento = document.getElementById(id);
          if (elemento) {
            elemento.addEventListener("click", handler);
          }
        }

        function mostraMessaggio(elemento, tipo, testo) {
          elemento.className = "messaggio " + tipo;
          elemento.textContent = testo;
          elemento.style.display = "block";
        }

        function nascondiMessaggio(elemento) {
          elemento.style.display = "none";
        }

        function salvaSocioLocale(dati) {
          localStorage.setItem(CHIAVE_SOCIO, JSON.stringify(dati));
        }

        function leggiSocioLocale() {
          try {
            const valore = localStorage.getItem(CHIAVE_SOCIO);
            return valore ? JSON.parse(valore) : null;
          } catch (errore) {
            console.log(errore);
            return null;
          }
        }

        function cancellaSocioLocale() {
          localStorage.removeItem(CHIAVE_SOCIO);
        }

        function leggiIdsUsciteNotificate() {
          try {
            const valore = localStorage.getItem(CHIAVE_USCITE_NOTIFICATE);
            const elenco = valore ? JSON.parse(valore) : [];
            return new Set(Array.isArray(elenco) ? elenco : []);
          } catch (errore) {
            console.log(errore);
            return new Set();
          }
        }

        function salvaIdsUsciteNotificate(ids) {
          localStorage.setItem(CHIAVE_USCITE_NOTIFICATE, JSON.stringify(Array.from(ids)));
        }

        function nomeCompletoSocio(dati) {
          return (dati.nome + " " + (dati.cognome || "")).trim();
        }

        function socioIdoneoAlleUscite(dati) {
          return Boolean(dati && dati.retta_annuale_in_regola && dati.certificato_medico_consegnato);
        }

        function motiviNonIdoneita(dati) {
          const motivi = [];
          if (!dati.retta_annuale_in_regola) {
            motivi.push("retta annuale non in regola");
          }
          if (!dati.certificato_medico_consegnato) {
            motivi.push("certificato medico mancante");
          }
          return motivi;
        }

        function combinaDataEOra(data, ora) {
          if (!data || !ora) return null;
          const oraNormalizzata = ora.length === 5 ? ora + ":00" : ora;
          return data + "T" + oraNormalizzata;
        }

        function aggiornaListaFotoDanni() {
          const etichetta = document.getElementById("foto-danni-selezionate");
          etichetta.textContent = fotoDanniSelezionate.length
            ? fotoDanniSelezionate.map((file) => file.name).join(", ")
            : "Nessuna foto selezionata.";
        }

        function aggiungiFotoDanni(fileList) {
          const fileNuovi = Array.from(fileList || []);
          if (!fileNuovi.length) {
            return;
          }
          fotoDanniSelezionate = fotoDanniSelezionate.concat(fileNuovi);
          aggiornaListaFotoDanni();
        }

        function resetFotoDanni() {
          fotoDanniSelezionate = [];
          document.getElementById("foto-danni-galleria").value = "";
          document.getElementById("foto-danni-fotocamera").value = "";
          aggiornaListaFotoDanni();
        }

        async function fetchJsonNoCache(url, options = {}) {
          let finalUrl = url;
          const metodo = (options.method || "GET").toUpperCase();
          if (metodo === "GET") {
            const separatore = url.includes("?") ? "&" : "?";
            finalUrl = url + separatore + "_ts=" + Date.now();
          }
          const headers = new Headers(options.headers || {});
          headers.set("Cache-Control", "no-store");
          headers.set("Pragma", "no-cache");
          const risposta = await fetch(finalUrl, { ...options, headers, cache: "no-store" });
          const dati = await risposta.json();
          return { risposta, dati };
        }

        function formattaDataOraItaliane(valore) {
          if (!valore) return "-";
          return new Date(valore).toLocaleString("it-IT");
        }

        function formattaDataIt(valore) {
          if (!valore) return "-";
          return new Date(valore).toLocaleDateString("it-IT");
        }

        function formattaOraIt(valore) {
          if (!valore) return "-";
          return new Date(valore).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" });
        }

        function parseEquipaggio(valore) {
          return (valore || "")
            .split(/[\\n,]+/)
            .map((nome) => nome.trim())
            .filter(Boolean);
        }

        function scorriA(elemento) {
          elemento.scrollIntoView({ behavior: "smooth", block: "start" });
        }

        async function attivaNotificheSePossibile() {
          if (!("Notification" in window)) {
            return;
          }
          if (Notification.permission === "default") {
            try {
              await Notification.requestPermission();
            } catch (errore) {
              console.log(errore);
            }
          }
        }

        function richiediLoginPerPrenotazioni() {
          document.getElementById("recupero-accesso").classList.remove("nascosto");
          mostraMessaggio(
            messaggioAccesso,
            "errore",
            "Per aprire le prenotazioni devi prima registrare questo telefono o collegare un profilo esistente."
          );
          scorriA(document.getElementById("login-socio"));
        }

        function apriPrenotazioni() {
          if (!socioCorrente) {
            richiediLoginPerPrenotazioni();
            return;
          }
          sezioneImbarcazioniCategorie.classList.add("nascosto");
          sezionePrenotazioni.classList.remove("nascosto");
          scorriA(sezionePrenotazioni);
        }

        async function apriRegistro() {
          sezioneImbarcazioniCategorie.classList.add("nascosto");
          sezioneRegistro.classList.remove("nascosto");
          await caricaRegistroUscite();
          scorriA(sezioneRegistro);
        }

        async function apriElencoImbarcazioni() {
          sezioneRegistro.classList.add("nascosto");
          sezioneImbarcazioniCategorie.classList.remove("nascosto");
          await caricaTutteLeImbarcazioni();
          scorriA(sezioneImbarcazioniCategorie);
        }

        function aggiornaTestata(dati) {
          document.getElementById("titolo-socio").textContent = "Benvenuto";
          document.getElementById("info-socio").innerHTML = "<strong>" + nomeCompletoSocio(dati) + "</strong>";
        }

        function aggiornaStatoIdoneita(dati) {
          const avviso = document.getElementById("avviso-idoneita");
          const pulsantePrenotazioni = document.getElementById("dashboard-prenotazioni");
          if (socioIdoneoAlleUscite(dati)) {
            nascondiMessaggio(avviso);
            pulsantePrenotazioni.disabled = false;
            pulsantePrenotazioni.title = "";
            return;
          }

          const motivi = motiviNonIdoneita(dati);
          mostraMessaggio(
            avviso,
            "errore",
            "Non puoi prenotare finche non sei in regola con: " + motivi.join(" e ") + "."
          );
          pulsantePrenotazioni.disabled = true;
          pulsantePrenotazioni.title = "Prenotazione bloccata: " + motivi.join(" e ");
        }

        function riempiProfilo(dati) {
          document.getElementById("profilo-nome").value = dati.nome || "";
          document.getElementById("profilo-cognome").value = dati.cognome || "";
          document.getElementById("profilo-telefono").value = dati.telefono || "";
          document.getElementById("profilo-ruolo").value = dati.ruolo || "allievo";
        }

        function mostraDashboard(dati) {
          socioCorrente = dati;
          salvaSocioLocale(dati);
          document.getElementById("dashboard-socio").classList.remove("nascosto");
          aggiornaTestata(dati);
          aggiornaStatoIdoneita(dati);
          riempiProfilo(dati);
          document.getElementById("profilo-socio").classList.add("nascosto");
          nascondiMessaggio(messaggioAccesso);
        }

        function mostraLogin() {
          document.getElementById("dashboard-socio").classList.add("nascosto");
          document.getElementById("dettaglio-barca").classList.add("nascosto");
          document.getElementById("profilo-socio").classList.add("nascosto");
          document.getElementById("recupero-accesso").classList.add("nascosto");
          sezioneRegistro.classList.add("nascosto");
          sezioneImbarcazioniCategorie.classList.add("nascosto");
          nascondiMessaggio(messaggioAccesso);
          nascondiMessaggio(messaggioAzione);
          nascondiMessaggio(document.getElementById("avviso-idoneita"));
          nascondiMessaggio(document.getElementById("avviso-notifiche"));
        }

        function renderTipologie() {
          const contenitore = document.getElementById("lista-tipologie");
          contenitore.innerHTML = "";
          for (const tipologia of TIPOLOGIE) {
            const bottone = document.createElement("button");
            bottone.type = "button";
            bottone.className = "tipologia-btn" + (tipologia === tipologiaCorrente ? " attiva" : "");
            bottone.textContent = ETICHETTE_TIPOLOGIE[tipologia] || tipologia;
            bottone.addEventListener("click", async () => {
              tipologiaCorrente = tipologia;
              renderTipologie();
              await caricaBarche();
            });
            contenitore.appendChild(bottone);
          }
        }

        function renderTipologieRegistro() {
          const contenitore = document.getElementById("lista-tipologie-registro");
          contenitore.innerHTML = "";
          for (const tipologia of TIPOLOGIE) {
            const bottone = document.createElement("button");
            bottone.type = "button";
            bottone.className = "tipologia-btn" + (tipologia === tipologiaRegistroCorrente ? " attiva" : "");
            bottone.textContent = ETICHETTE_TIPOLOGIE[tipologia] || tipologia;
            bottone.addEventListener("click", () => {
              tipologiaRegistroCorrente = tipologia;
              renderTipologieRegistro();
              renderRegistroUscite();
            });
            contenitore.appendChild(bottone);
          }
        }

        function mostraNotificaUscita(uscita) {
          if (!("Notification" in window) || Notification.permission !== "granted") {
            return;
          }
          const corpo = (uscita.organizzatore || "Un socio") + " ha prenotato " + uscita.barca + ". Apri l'app per vedere i dettagli.";
          new Notification("Nuova uscita al circolo", {
            body: corpo,
            icon: "/icona-app.svg"
          });
        }

        function aggiornaNotificheUscite(uscite) {
          const avviso = document.getElementById("avviso-notifiche");
          const nuovi = [];
          for (const uscita of uscite) {
            if (!idsUsciteNotificate.has(uscita.id)) {
              idsUsciteNotificate.add(uscita.id);
              const socioAttuale = socioCorrente ? nomeCompletoSocio(socioCorrente) : "";
              if (uscita.organizzatore !== socioAttuale) {
                nuovi.push(uscita);
              }
            }
          }

          if (!notificheUsciteInizializzate) {
            notificheUsciteInizializzate = true;
            salvaIdsUsciteNotificate(idsUsciteNotificate);
            return;
          }

          if (!nuovi.length) {
            salvaIdsUsciteNotificate(idsUsciteNotificate);
            return;
          }

          const ultima = nuovi[nuovi.length - 1];
          mostraMessaggio(
            avviso,
            "successo",
            "Nuova uscita aperta al circolo: " + ultima.barca + " prenotata da " + ultima.organizzatore + "."
          );
          for (const uscita of nuovi) {
            mostraNotificaUscita(uscita);
          }
          salvaIdsUsciteNotificate(idsUsciteNotificate);
        }

        async function caricaBarche() {
          const { risposta, dati } = await fetchJsonNoCache("/risorse/stato?tipologia=" + encodeURIComponent(tipologiaCorrente));
          barcheCorrenti = risposta.ok ? dati : [];
          renderBarche();
        }

        async function caricaTutteLeImbarcazioni() {
          const contenitore = document.getElementById("lista-imbarcazioni-categorie");
          contenitore.innerHTML = "";
          for (const tipologia of TIPOLOGIE) {
            const { risposta, dati } = await fetchJsonNoCache("/risorse/stato?tipologia=" + encodeURIComponent(tipologia));
            const barche = risposta.ok ? dati : [];
            const sezione = document.createElement("div");
            sezione.className = "categoria-imbarcazioni";
            const titolo = document.createElement("h4");
            titolo.textContent = ETICHETTE_TIPOLOGIE[tipologia] || tipologia;
            sezione.appendChild(titolo);

            const griglia = document.createElement("div");
            griglia.className = "griglia-barche";

            if (!barche.length) {
              griglia.innerHTML = "<div class='barca'>Nessuna imbarcazione presente in questa categoria.</div>";
            } else {
              for (const barca of barche) {
                const box = document.createElement("div");
                box.className = "barca " + (barca.occupata ? "occupata" : "libera");
                const stato = barca.occupata ? "Occupata" : "Libera";
                const dettaglio = barca.occupata
                  ? "<br>Prenotata da: " + (barca.organizzatore || "-")
                  : "<br>Disponibile";
                box.innerHTML = "<strong>" + barca.nome + "</strong><br><span class='stato " + (barca.occupata ? "occupata" : "libera") + "'>" + stato + "</span>" + dettaglio;
                box.addEventListener("click", () => apriBarca(barca));
                griglia.appendChild(box);
              }
            }

            sezione.appendChild(griglia);
            contenitore.appendChild(sezione);
          }
        }

        function renderBarche() {
          const contenitore = document.getElementById("elenco-barche");
          contenitore.innerHTML = "";
          if (!barcheCorrenti.length) {
            contenitore.innerHTML = "<div class='barca'>Nessuna imbarcazione presente in questa tipologia.</div>";
            return;
          }
          for (const barca of barcheCorrenti) {
            const box = document.createElement("div");
            box.className = "barca " + (barca.occupata ? "occupata" : "libera") + (barcaSelezionata && barcaSelezionata.id === barca.id ? " selezionata" : "");
            const stato = barca.occupata ? "Occupata" : "Libera";
            const dettaglio = barca.occupata
              ? "<br>Prenotata da: " + (barca.organizzatore || "-") + "<br>Partenza: " + formattaDataOraItaliane(barca.ora_partenza || barca.ora_partenza_effettiva) + "<br>Arrivo: " + formattaDataOraItaliane(barca.ora_rientro_prevista || barca.ora_rientro_effettiva)
              : "<br>Seleziona per prenotare";
            box.innerHTML = "<strong>" + barca.nome + "</strong><br><span class='stato " + (barca.occupata ? "occupata" : "libera") + "'>" + stato + "</span>" + dettaglio;
            box.addEventListener("click", () => apriBarca(barca));
            contenitore.appendChild(box);
          }
        }

        function apriBarca(barca) {
          barcaSelezionata = barca;
          renderBarche();
          document.getElementById("dettaglio-barca").classList.remove("nascosto");
          document.getElementById("titolo-barca").textContent = barca.nome;
          document.getElementById("riepilogo-occupazione").classList.add("nascosto");
          document.getElementById("data-prenotazione").value = barca.data_prenotazione
            ? new Date(barca.data_prenotazione).toISOString().slice(0, 10)
            : new Date().toISOString().slice(0, 10);
          document.getElementById("equipaggio-barca").value = (barca.persone_imbarcate || []).join(", ");
          document.getElementById("equipaggio-barca").readOnly = false;
          document.getElementById("chiusura-ora-partenza").value = "";
          document.getElementById("chiusura-ora-rientro").value = "";
          document.getElementById("nota-prenotazione").value = barca.occupata ? (barca.nota || "") : "";
          document.getElementById("nota-rientro").value = "";
          document.getElementById("danni-rientro").value = "";
          resetFotoDanni();
          document.getElementById("form-prenotazione").classList.toggle("nascosto", barca.occupata);
          document.getElementById("form-rientro").classList.add("nascosto");

          if (barca.occupata) {
            document.getElementById("stato-barca").innerHTML =
              "<div class='messaggio errore' style='display:block;'>Questa barca e occupata da " + (barca.organizzatore || "un socio") + ".</div>";
            document.getElementById("riepilogo-occupazione").classList.remove("nascosto");
            document.getElementById("orario-partenza-attivo").textContent = formattaDataOraItaliane(barca.ora_partenza || barca.ora_partenza_effettiva);
            document.getElementById("orario-arrivo-attivo").textContent = formattaDataOraItaliane(barca.ora_rientro_prevista || barca.ora_rientro_effettiva);
            if (socioCorrente && barca.organizzatore === nomeCompletoSocio(socioCorrente)) {
              document.getElementById("form-rientro").classList.remove("nascosto");
            }
          } else {
            document.getElementById("stato-barca").innerHTML =
              "<div class='messaggio successo' style='display:block;'>Questa barca e libera.</div>";
          }
          scorriA(document.getElementById("dettaglio-barca"));
        }

        async function caricaUsciteAperte() {
          const contenitore = document.getElementById("lista-uscite");
          const { risposta, dati } = await fetchJsonNoCache("/prenotazioni/disponibili");
          const uscite = risposta.ok ? dati : [];
          aggiornaNotificheUscite(uscite);
          contenitore.innerHTML = "";
          if (!uscite.length) {
            contenitore.innerHTML = "<div class='uscita'>Al momento non ci sono uscite aperte al circolo.</div>";
            return;
          }
          for (const uscita of uscite) {
            const box = document.createElement("div");
            box.className = "uscita";
            const equipaggio = uscita.persone_imbarcate && uscita.persone_imbarcate.length
              ? uscita.persone_imbarcate.join(", ")
              : "Non indicato";
            const nota = uscita.nota ? "<br>Nota: " + uscita.nota : "";
            box.innerHTML =
              "<strong>" + uscita.barca + "</strong><br>" +
              "Data prenotazione: " + formattaDataIt(uscita.inizio) + "<br>" +
              "Ora di partenza: " + formattaOraIt(uscita.inizio) + "<br>" +
              "Ora di arrivo: " + formattaOraIt(uscita.fine) + "<br>" +
              "Capo barca: " + uscita.organizzatore + "<br>" +
              "Equipaggio: " + equipaggio +
              nota;
            contenitore.appendChild(box);
          }
        }

        function renderRegistroUscite() {
          const contenitore = document.getElementById("lista-registro-uscite");
          contenitore.innerHTML = "";
          const righe = registroUsciteCorrente.filter((uscita) => (uscita.tipologia || "derive") === tipologiaRegistroCorrente);
          if (!righe.length) {
            contenitore.innerHTML = "<div class='riga-registro'>Nessuna uscita registrata in questa categoria.</div>";
            return;
          }
          for (const uscita of righe) {
            const box = document.createElement("div");
            box.className = "riga-registro";
            const equipaggioSalvato = Array.isArray(uscita.persone_imbarcate) ? uscita.persone_imbarcate : [];
            const equipaggioCompleto = [uscita.organizzatore].concat(
              equipaggioSalvato.filter((nome) => nome && nome !== uscita.organizzatore)
            );
            const equipaggio = "<br>Equipaggio: " + equipaggioCompleto.join(", ");
            const nota = uscita.nota ? "<br>Nota uscita: " + uscita.nota : "";
            const notaFinale = uscita.nota_rientro ? "<br>Nota finale: " + uscita.nota_rientro : "";
            const danni = uscita.danni ? "<br>Danni: " + uscita.danni : "";
            const foto = uscita.foto_danni && uscita.foto_danni.length
              ? "<br>Foto danni: " + uscita.foto_danni.map((foto) => "<a href='" + foto + "' target='_blank'>apri foto</a>").join(" | ")
              : "";
            const partenza = uscita.ora_partenza ? formattaDataOraItaliane(uscita.ora_partenza) : "-";
            const arrivo = uscita.ora_arrivo ? formattaDataOraItaliane(uscita.ora_arrivo) : "-";
            const stato = uscita.chiusa ? "Chiusa" : "Aperta";
            box.innerHTML =
              "<strong>" + uscita.barca + "</strong><br>" +
              "Capo barca: " + uscita.organizzatore + "<br>" +
              "Data: " + uscita.data_uscita + "<br>" +
              "Ora di partenza: " + partenza + "<br>" +
              "Ora di arrivo: " + arrivo +
              equipaggio + nota + notaFinale + danni + foto +
              "<br><span class='stato-registro'>" + stato + "</span>";
            contenitore.appendChild(box);
          }
        }

        async function caricaRegistroUscite() {
          const { risposta, dati } = await fetchJsonNoCache("/registro-uscite");
          registroUsciteCorrente = risposta.ok ? dati : [];
          renderTipologieRegistro();
          renderRegistroUscite();
        }

        async function caricaFotoDanni() {
          if (!fotoDanniSelezionate.length) {
            return [];
          }
          const formData = new FormData();
          for (const file of fotoDanniSelezionate) {
            formData.append("foto", file);
          }
          const risposta = await fetch("/prenotazioni/carica-foto-danni", {
            method: "POST",
            body: formData
          });
          const dati = await risposta.json();
          if (!risposta.ok) {
            throw new Error(dati.detail || "Caricamento foto non riuscito.");
          }
          return dati;
        }

        collegaClick("nav-registrati", () => {
          window.location.href = "/registrazione-socio";
        });

        collegaClick("nav-modifica-dati", () => {
          if (!socioCorrente) {
            richiediLoginPerPrenotazioni();
            return;
          }
          document.getElementById("dashboard-socio").classList.remove("nascosto");
          document.getElementById("profilo-socio").classList.remove("nascosto");
          scorriA(document.getElementById("dashboard-socio"));
        });

        collegaClick("nav-contatti", () => {
          scorriA(sezioneContatti);
        });

        collegaClick("nav-amministratore", () => {
          window.location.href = "/amministrazione";
        });

        collegaClick("dashboard-prenotazioni", () => {
          attivaNotificheSePossibile();
          apriPrenotazioni();
        });

        collegaClick("dashboard-registro", async () => {
          attivaNotificheSePossibile();
          await apriRegistro();
        });

        collegaClick("chiudi-registro-uscite", () => {
          sezioneRegistro.classList.add("nascosto");
        });

        document.getElementById("vai-registrazione").addEventListener("click", () => {
          window.location.href = "/registrazione-socio";
        });

        document.getElementById("mostra-recupero").addEventListener("click", () => {
          document.getElementById("recupero-accesso").classList.toggle("nascosto");
        });

        collegaClick("dashboard-regolamento", () => {
          window.open("/regolamento?ts=" + Date.now(), "_blank", "noopener");
        });

        document.getElementById("apri-galleria").addEventListener("click", () => {
          document.getElementById("foto-danni-galleria").click();
        });

        document.getElementById("apri-fotocamera").addEventListener("click", () => {
          document.getElementById("foto-danni-fotocamera").click();
        });

        document.getElementById("foto-danni-galleria").addEventListener("change", (evento) => {
          aggiungiFotoDanni(evento.target.files);
        });

        document.getElementById("foto-danni-fotocamera").addEventListener("change", (evento) => {
          aggiungiFotoDanni(evento.target.files);
        });

        document.getElementById("entra-socio").addEventListener("click", async () => {
          const payload = {
            email: document.getElementById("accesso-email").value.trim() || null,
            numero_tessera_fiv: document.getElementById("accesso-tessera").value.trim() || null
          };
          const risposta = await fetch("/utenti/accesso", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const dati = await risposta.json();
          if (!risposta.ok) {
            mostraMessaggio(messaggioAccesso, "errore", dati.detail || "Accesso non riuscito.");
            return;
          }
          await attivaNotificheSePossibile();
          mostraDashboard(dati);
          renderTipologie();
          await caricaBarche();
          await caricaUsciteAperte();
          scorriA(document.getElementById("dashboard-socio"));
        });

        collegaClick("apri-profilo", () => {
          document.getElementById("profilo-socio").classList.toggle("nascosto");
        });

        document.getElementById("salva-profilo").addEventListener("click", async () => {
          if (!socioCorrente) return;
          const payload = {
            nome: document.getElementById("profilo-nome").value.trim(),
            cognome: document.getElementById("profilo-cognome").value.trim(),
            email: socioCorrente.email || null,
            telefono: document.getElementById("profilo-telefono").value.trim() || null,
            numero_tessera_fiv: socioCorrente.numero_tessera_fiv || null,
            retta_annuale_in_regola: Boolean(socioCorrente.retta_annuale_in_regola),
            certificato_medico_consegnato: Boolean(socioCorrente.certificato_medico_consegnato),
            ruolo: document.getElementById("profilo-ruolo").value
          };
          const risposta = await fetch("/utenti/" + socioCorrente.id, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const dati = await risposta.json();
          if (!risposta.ok) {
            mostraMessaggio(messaggioAzione, "errore", dati.detail || "Aggiornamento non riuscito.");
            return;
          }
          mostraDashboard(dati);
          renderTipologie();
          await caricaBarche();
          mostraMessaggio(messaggioAzione, "successo", "Dati aggiornati correttamente.");
        });

        document.getElementById("conferma-prenotazione").addEventListener("click", async () => {
          if (!socioCorrente || !barcaSelezionata) return;
          const data = document.getElementById("data-prenotazione").value;
          const inizio = combinaDataEOra(data, "00:00");
          const fine = combinaDataEOra(data, "23:59");
          if (!inizio || !fine) {
            mostraMessaggio(messaggioAzione, "errore", "Inserisci la data dell'uscita.");
            return;
          }
          const payload = {
            id_creatore: socioCorrente.id,
            id_risorsa: barcaSelezionata.id,
            inizio,
            fine,
            persone_imbarcate: parseEquipaggio(document.getElementById("equipaggio-barca").value),
            nota: document.getElementById("nota-prenotazione").value.trim() || null,
            danni: null,
            aperta_al_circolo: true
          };
          const risposta = await fetch("/prenotazioni", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const dati = await risposta.json();
          if (!risposta.ok) {
            mostraMessaggio(messaggioAzione, "errore", dati.detail || "Prenotazione non riuscita.");
            return;
          }
          mostraMessaggio(messaggioAzione, "successo", "Prenotazione confermata.");
          document.getElementById("dettaglio-barca").classList.add("nascosto");
          barcaSelezionata = null;
          await caricaBarche();
          await caricaUsciteAperte();
          await caricaRegistroUscite();
        });

        document.getElementById("chiudi-prenotazione").addEventListener("click", async () => {
          if (!barcaSelezionata || !barcaSelezionata.id_prenotazione_attiva) return;
          const oraPartenza = document.getElementById("chiusura-ora-partenza").value;
          const ora = document.getElementById("chiusura-ora-rientro").value;
          const dataPartenza = (barcaSelezionata.ora_partenza || barcaSelezionata.data_prenotazione || "").slice(0, 10);
          const dataArrivo = (barcaSelezionata.ora_rientro_prevista || barcaSelezionata.data_prenotazione || "").slice(0, 10);
          const partenza = combinaDataEOra(dataPartenza, oraPartenza);
          const rientro = combinaDataEOra(dataArrivo, ora);
          if (!partenza || !rientro) {
            mostraMessaggio(messaggioAzione, "errore", "Inserisci ora di partenza e ora di arrivo.");
            return;
          }
          let fotoDanni = [];
          try {
            fotoDanni = await caricaFotoDanni();
          } catch (errore) {
            mostraMessaggio(messaggioAzione, "errore", errore.message || "Caricamento foto non riuscito.");
            return;
          }
          const payload = {
            ora_partenza_effettiva: partenza,
            ora_rientro_effettiva: rientro,
            persone_imbarcate: parseEquipaggio(document.getElementById("equipaggio-barca").value),
            nota_rientro: document.getElementById("nota-rientro").value.trim() || null,
            danni: document.getElementById("danni-rientro").value.trim() || null,
            foto_danni: fotoDanni
          };
          const risposta = await fetch("/prenotazioni/" + barcaSelezionata.id_prenotazione_attiva + "/chiusura", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const dati = await risposta.json();
          if (!risposta.ok) {
            mostraMessaggio(messaggioAzione, "errore", dati.detail || "Chiusura rientro non riuscita.");
            return;
          }
          mostraMessaggio(messaggioAzione, "successo", "Rientro confermato. La barca e tornata disponibile.");
          document.getElementById("dettaglio-barca").classList.add("nascosto");
          document.getElementById("riepilogo-occupazione").classList.add("nascosto");
          barcaSelezionata = null;
          await caricaBarche();
          await caricaUsciteAperte();
          await caricaRegistroUscite();
        });

        mostraLogin();
        idsUsciteNotificate = leggiIdsUsciteNotificate();
        renderTipologie();
        renderTipologieRegistro();
        caricaUsciteAperte();
        caricaRegistroUscite();

        const parametriPagina = new URLSearchParams(window.location.search);
        if (parametriPagina.get("reset") === "1") {
          cancellaSocioLocale();
          window.history.replaceState({}, document.title, window.location.pathname);
        }

        setInterval(async () => {
          await caricaUsciteAperte();
          if (!sezioneRegistro.classList.contains("nascosto")) {
            await caricaRegistroUscite();
          }
          if (!sezionePrenotazioni.classList.contains("nascosto")) {
            await caricaBarche();
          }
        }, 15000);

        const socioSalvato = leggiSocioLocale();
        if (socioSalvato && socioSalvato.id) {
          mostraDashboard(socioSalvato);
          caricaBarche();
        }
      </script>
    </body>
    </html>
    """
    logo = CONFIGURAZIONE_APP["logo"]
    home = CONFIGURAZIONE_APP["home"]
    contatti = CONFIGURAZIONE_APP["contatti"]
    orari = CONFIGURAZIONE_APP["orari"]
    etichette = CONFIGURAZIONE_APP["etichette"]
    percorso_logo = PERCORSO_BASE / "assets" / "logo-prenotazioni-imbarcazioni.svg"
    logo_personalizzato_standard = (
        str(logo.get("riga_1", "")).strip().upper() == "PRENOTAZIONI"
        and str(logo.get("riga_2", "")).strip().upper() == "IMBARCAZIONI"
        and str(logo.get("riga_3", "")).strip().upper() in {"APP", ""}
    )
    if percorso_logo.exists() and logo_personalizzato_standard:
        logo_markup = (
            '<img class="logo-immagine" src="/logo-app.svg?v=1" '
            'alt="Prenotazioni Imbarcazioni">'
        )
    else:
        logo_markup = (
            f'<span class="grande">{logo["riga_1"]}</span>\n'
            f'            <span class="medio">{logo["riga_2"]}</span>\n'
            f'            <span class="vela">{logo["riga_3"]}</span>'
        )
    feriali = orari["feriali"]
    festivi = orari["festivi"]
    blocco_feriali = (
        f'{feriali["giorni"]}<br>\n'
        f'                  Apertura: {feriali["apertura"]}<br>\n'
        f'                  Chiusura: {feriali["chiusura"]}'
    )
    blocco_festivi = (
        f'{festivi["giorni"]}<br>\n'
        f'                  Apertura: {festivi["apertura"]}<br>\n'
        f'                  Chiusura: {festivi["chiusura"]}'
    )
    return (
        pagina.replace("__CONFIGURAZIONE_APP__", configurazione_frontend_json())
        .replace("__TITOLO_AREA_SOCIO__", f"{CONFIGURAZIONE_APP['nome_app']} - Registro uscite")
        .replace("__LOGO_APP__", logo_markup)
        .replace("__HOME_EYEBROW__", str(home["eyebrow"]))
        .replace("__HOME_TITOLO__", str(home["titolo"]))
        .replace("__HOME_SOTTOTITOLO__", str(home["sottotitolo"]))
        .replace("__HOME_TESTO__", str(home["testo"]))
        .replace("__ETICHETTA_TESSERA__", str(etichette["tessera"]))
        .replace("__ETICHETTA_QUOTA__", str(etichette["quota_annuale"]))
        .replace("__ETICHETTA_CERTIFICATO__", str(etichette["certificato_medico"]))
        .replace("__ORARI_TITOLO__", str(orari["titolo"]))
        .replace("__ORARI_SEDE_TITOLO__", str(orari["sede_titolo"]))
        .replace("__ORARI_SERVIZIO_TITOLO__", str(orari["servizio_titolo"]))
        .replace("__ORARI_FERIALI__", blocco_feriali)
        .replace("__ORARI_FESTIVI__", blocco_festivi)
        .replace("__CONTATTI_DESCRIZIONE__", "Riferimenti principali personalizzabili.")
        .replace("__CONTATTI_TELEFONO_TITOLO__", str(contatti["titolo_telefono"]))
        .replace("__CONTATTI_TELEFONO_LABEL__", str(contatti["telefono_label"]))
        .replace("__CONTATTI_TELEFONO__", str(contatti["telefono"]))
        .replace("__CONTATTI_TELEFONO_VISIBILE__", str(contatti["telefono_visibile"]))
        .replace("__CONTATTI_EMAIL__", str(contatti["email"]))
        .replace("__CONTATTI_LUOGO__", str(contatti["luogo"]))
        .replace("__CONTATTI_CITTA__", str(contatti["citta"]))
    )
