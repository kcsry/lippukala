/* globals PosQR */

/**
 * @typedef {Object} Code
 * @property {boolean} used
 * @property {string|null} used_ts
 * @property {number} id
 * @property {string} [name]
 * @property {string} code
 * @property {string} comment
 * @property {string} lit
 * @property {string} prefix
 * @property {string} prod
 */

/**
 * @typedef {Object} CodesResponse
 * @property {Code[]} codes
 */

/** @type {Code|null} */
let codeToConfirm = null;

/** @type {Record<number, Code>} */
const codes = {};

/**
 * A set of all code IDs used locally (not persistent
 * between reloads)
 * @type {Set<number>}
 */
const codeIdsUsedLocally = new Set();

/** @type {number[]} */
let useQueue = [];

/** @type {number|null} */
let currentlyShownId = null;

/** The current year, as a string. */
const thisYearString = String(new Date().getFullYear());

/** @type {PosQR|null} */
let posQR = null;

/**
 * @param {string} id ID or selector
 * @returns {HTMLElement}
 */
function $(id) {
  const el = document.getElementById(id) ?? document.querySelector(id);
  if (!el) throw new Error(`Element ${id} not found`);
  return el;
}

function addLogEntry(string) {
  const time = new Date().toLocaleTimeString("fi-FI");
  const messageWithTime = `${time}: ${string}\n`;
  const logTextArea = $("log");
  logTextArea.value += messageWithTime;
  logTextArea.scroll(0, 90000);
}

/**
 * @param {CodesResponse} data
 */
function parseData(data) {
  for (const code of data.codes) {
    codes[code.id] = { ...(codes[code.id] || {}), ...code };
  }
}

async function download() {
  const jsonUrl = `?json=1&t=${Math.round(+new Date())}`;
  const response = await fetch(jsonUrl);
  if (!response.ok) throw new Error(`Failed to fetch ${jsonUrl}`);
  const data = await response.json();
  parseData(data);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function shortenName(name) {
  if (name) {
    const [word1, word2] = name.trim().split(/\s+/);
    return `${word1} ${word2[0]}.`;
  }
  return "";
}

function Tee(template, env) {
  return template.replace(/\{(.+?)\}/g, (_, m) => escapeHtml(env[m] || "").replace(/\n/g, "<br>"));
}

/**
 * @param code {Code}
 */
function isCodeLocallyUsed(code) {
  return codeIdsUsedLocally.has(code.id);
}

function getCodeCSSClass(code) {
  const isLocallyUsed = isCodeLocallyUsed(code);
  if (code.used) {
    return isLocallyUsed ? "code-used-here" : "code-used";
  }
  return isLocallyUsed ? "code-used-not-synced" : "code-unused";
}

function getCodeStatusText(code) {
  const prettierTime = code.used_ts ? code.used_ts.replace(/T/, "\u2009") : "";
  if (isCodeLocallyUsed(code)) {
    return `Käytetty tässä ${prettierTime}`;
  }
  if (code.used) {
    return `Käytetty ${prettierTime}`;
  }
  return "Ei käytetty";
}

/**
 * Return if the code seems to be for a product that is not for this year.
 * @param code {Code}
 */
function isPossiblyOldCode(code) {
  const yearMatch = /\b(20\d{2})\b/g.exec(code.prod);
  return yearMatch && yearMatch[1] !== thisYearString;
}

/**
 * @param {Code|null} code
 */
function showCode(code) {
  const statusDiv = $("#status");
  const acceptBtn = $("#accept-btn");
  if (code) {
    currentlyShownId = code.id;
    statusDiv.innerHTML = Tee(
      "<div class=cd><span class=pfx>{prefix}</span>{code}</div>{lit}<div class=product>{prod}</div><div class=statustext>{statusText}</div></div><div class=addr>{short_name}<div class=fulladdr>{name}</div></div><div class=comment>{comment}</div>",
      { ...code, short_name: shortenName(code.name), statusText: getCodeStatusText(code) },
    );
    statusDiv.classList.toggle("check-year", isPossiblyOldCode(code));
    document.body.className = getCodeCSSClass(code);
    acceptBtn.disabled = !!code.used;
  } else {
    currentlyShownId = null;
    statusDiv.innerHTML = "";
    document.body.className = "";
    acceptBtn.disabled = true;
  }
}

/**
 * @param {Code} code
 */
function useCode(code) {
  codeIdsUsedLocally.add(code.id);
  useQueue.push(code.id);
  showCode(code);
}

/**
 * @param {Code} code
 */
function confirmUseCode(code) {
  if (code.used || code.localUsed) {
    alert("Koodi näyttää jo käytetyltä!\nOta yhteys tapahtuman taloustiimiin asian selvittämiseksi.");
    return;
  }
  codeToConfirm = code;
  $("#confirm-dialog").showModal();
  $("#confirm-button").focus();
}

function clearAndRefocusCodeInput() {
  const codeInput = $("#code");
  codeInput.value = "";
  codeInput.focus();
}

/**
 * Form submit handler for the confirm form dialog.
 */
function onConfirmCode() {
  const code = codeToConfirm;
  if (!code) {
    alert("Koodi puuttuu, kummaa!");
    return;
  }
  codeToConfirm = null;
  useCode(code);
  setTimeout(syncUseQueue, 4);
  setTimeout(clearAndRefocusCodeInput, 250);
}

/**
 * Find matching codes for the given input code.
 *
 * @param {string} inputCode
 * @returns {nMatches: number, code: Code | null}
 */
function findMatchingCodes(inputCode) {
  let nMatches = 0;
  let regexpText = `^${inputCode}`;
  if (/^[-a-z]+ /i.test(inputCode)) {
    // Cheap "fuzzy" searching ("d bu" will match "desu butler")
    regexpText = `^${inputCode
      .split(/\s+/)
      .filter((word) => word.length > 0)
      .join("[^ ]*? ")}`;
    regexpText = regexpText.replace(/\s+$/, "");
  }
  const searchRegexp = new RegExp(regexpText, "i");
  let lastCode = null;
  for (const code of Object.values(codes)) {
    const prefixedCode = (code.prefix || "") + code.code;
    if (
      inputCode === code.code ||
      inputCode === prefixedCode ||
      inputCode === code.lit.toLowerCase() ||
      searchRegexp.test(code.code) ||
      searchRegexp.test(prefixedCode) ||
      searchRegexp.test(code.lit)
    ) {
      nMatches++;
      lastCode = code;
    }
  }
  return { nMatches, code: nMatches === 1 ? lastCode : null };
}

function search(enter) {
  const statusDiv = $("#status");
  const inputCode = $("#code").value.toLowerCase().trim();
  const clearBtn = $("#clear-btn");
  if (!inputCode.length) {
    clearBtn.disabled = true;
    showCode(null);
    statusDiv.innerHTML = "";
    return;
  }
  clearBtn.disabled = false;
  const { nMatches, code } = findMatchingCodes(inputCode);
  if (nMatches === 1) {
    showCode(code);
    if (enter) confirmUseCode(code);
  } else if (nMatches === 0) {
    showCode(null);
    statusDiv.innerHTML = "Koodilla ei löydy yhtään lippua. Ole hyvä ja tarkista oikeinkirjoitus ja tapahtuma!";
  } else {
    showCode(null);
    statusDiv.innerHTML = `... ${nMatches} ...`;
  }
}

function formSubmit(event) {
  event.preventDefault();
  search(true);
}

function cancelConfirm() {
  const confirmDialog = $("#confirm-dialog");
  if (confirmDialog.open) confirmDialog.close();
  $("#code").focus();
}

async function syncUseQueue() {
  useQueue = useQueue.filter((id) => isCodeLocallyUsed(codes[id]) && !codes[id].used);
  if (!useQueue.length) {
    return;
  }
  const formData = new FormData();
  formData.append("use", useQueue.join(","));
  // eslint-disable-next-line no-restricted-globals
  const resp = await fetch(location.href, {
    method: "POST",
    body: formData,
  });
  if (!resp.ok) {
    addLogEntry("Koodien synkronointi epäonnistui");
    throw new Error(`Failed to sync use queue`);
  }
  const data = await resp.json();
  addLogEntry(`Käytettiin ${useQueue.length} koodia`);
  parseData(data);
  if (currentlyShownId) showCode(codes[currentlyShownId]);
}

function debounce(fn, delay) {
  let timer = null;
  return function () {
    const clear = function () {
      timer = null;
    };
    if (timer === null) {
      fn.apply(this, arguments); // eslint-disable-line prefer-rest-params
    } else {
      arguments[0].preventDefault(); // eslint-disable-line prefer-rest-params
    }
    window.clearTimeout(timer);
    timer = window.setTimeout(clear, delay);
  };
}

async function handleCameraClick() {
  if (!posQR) {
    posQR = new PosQR({
      addLogEntry,
      onFoundQRCode: ({ rawValue }) => {
        const text = rawValue.trim();
        if (/^\d+$/.test(text)) {
          $("#code").value = text;
          search(true);
        } else {
          this.addLogEntry(`QR-koodi ei ole numero: ${text}`);
        }
      },
    });
  }
  if (posQR.isStarted()) {
    await posQR.stop();
  } else {
    await posQR.start();
  }
  $("#camera-btn").classList.toggle("started", posQR.isStarted());
}

window.init = async function init() {
  showCode(null); // reset dom state
  search(false); // reset dom state
  await download();
  addLogEntry(`${Object.keys(codes).length} koodia`);
  setInterval(download, (50 + Math.random() * 20) * 1000);
  setInterval(syncUseQueue, 5000);
  $("#code").addEventListener("input", () => search(false), true);
  $("#codeform").addEventListener("submit", debounce(formSubmit, 250), true);
  $("#confirm-form").addEventListener("submit", onConfirmCode, true);
  $("#confirm-dialog").addEventListener("close", cancelConfirm, true);
  $("#camera-btn").addEventListener("click", () => handleCameraClick(), true);
  if (!PosQR.hasBarcodeDetector()) {
    $("#camera-btn").hidden = true;
  }
  $("#clear-btn").addEventListener(
    "click",
    () => {
      clearAndRefocusCodeInput();
      search(false);
    },
    true,
  );
};
