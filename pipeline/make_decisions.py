"""Manual (Claude-reviewed) relevance decisions. Edit the lists below and re-run to regenerate data/review_decisions.json.

PI=prompt-injection LS=llm-security ADV=adversarial-ml AL=alignment INT=interpretability
RISK=ai-risk PRIV=privacy DF=deepfakes-misuse GOV=governance
"""
import json
from pathlib import Path

PI, LS, ADV, AL, INT, RISK, PRIV, DF, GOV = ("prompt-injection", "llm-security", "adversarial-ml", "alignment",
                                             "interpretability", "ai-risk", "privacy", "deepfakes-misuse", "governance")
JB, CYBER, RT, SE = "jailbreaks", "ai-cyber", "red-teaming", "safety-evals"
INCLUDE = {
    # --- review queue picks ---
    "1sd26pWhfmg": [LS], "L5pUA3LsEaw": [AL], "xoVJKj8lcNQ": [RISK], "hEUO6pjwFOo": [AL], "NnV_cWeoo5Q": [LS],
    "viJt_DXTfwA": [AL], "O-2tpwW0kmU": [DF, RISK], "9CO6M2HsoIA": [DF, RISK], "kErHiET5YPw": [RISK], "h0962biiZa4": [RISK],
    "zkbPdEHEyEI": [AL], "xfMQ7hzyFW4": [RISK], "hhiLw5Q_UFg": [AL], "ISkAkiAkK7A": [RISK, AL], "LWiM-LuRe6w": [RISK],
    "tcdVC4e6EV4": [RISK], "kMLKbhY0ji0": [RISK], "GyFkWb903aU": [AL], "7PKx3kS7f4A": [AL], "540vzMlf-54": [RISK],
    "nKJlF-olKmg": [AL], "-p2il-V-0fk": [ADV], "5qfIgCiYlfY": [RISK], "144uOfr4SYA": [RISK], "7xij6SoCClI": [GOV, RISK],
    "Pp9MwZkHiMQ": [ADV], "Xx4Tpsk_fnM": [AL], "JAcwtV_bFp4": [AL], "YhgYMH6n004": [DF], "ZdhyM5jHu0s": [GOV],
    "6n2eDcRjSsk": [DF, LS], "NxOehfOfB6c": [LS], "B_7RpP90rUk": [LS], "mUfJOQKdtAk": [DF], "-JlxuQ7tPgQ": [RISK],
    "giT0ytynSqg": [RISK], "X50zezLFWWI": [RISK], "kopoLzvh5jY": [AL], "Ao4jwLwT36M": [AL], "5KVDDfAkRgc": [RISK],
    "RheZlFj3Zp8": [RISK], "D8GOeCFFby4": [INT], "qrvK_KuIeJk": [RISK], "GYQrNfSmQ0M": [RISK], "L_1plTXF-FE": [PI],
    "tr1tTJk32uk": [PI, LS], "-YJgcTCSzU0": [PI, LS], "5TFn13QOpU4": [LS], "8rptE4vVWn4": [LS], "GJVSDjRXVoo": [PI],
    "BwltbhR0JgU": [PI], "WvmeTaFc_Qw": [AL], "VcVfceTsD0A": [RISK, GOV], "XcNlv9gp20o": [RISK], "0pgEMWy70Qk": [AL],
    "-TnsQHdI4eo": [RISK], "7wy3xyoXYt8": [RISK], "luXnftoxCaM": [RISK], "XnnjvIqf4fU": [AL], "Gw_hnD7m00M": [RISK],
    "VRjgNgJms3Q": [AL], "WX_vN1QYgmE": [RISK],
    "BtnvfVc8z8o": [AL], "sZzcSX7BFVA": [LS], "piYnd_wYlT8": [ADV], "zQ_uMenoBCk": [ADV], "HvZAZFztlO0": [ADV],
    "-OdOmU58zOw": [ADV], "kaExCim2H9s": [ADV, LS], "1cSw4fXYqWI": [ADV], "6ROlMFlbkWE": [PRIV], "7bx9UfDHf_k": [LS],
    "PrSYYaZCxsc": [LS], "8rOY3aD1yxY": [LS], "_UAlYumHLQQ": [LS], "927W6zzvV-c": [LS], "-3p2F5HWdSY": [LS],
    "ldEJq_JxYuM": [GOV], "_3okhTwa7w4": [LS], "GnO4dRHBzKI": [GOV], "F6HSsVIkqIU": [DF], "7XchCsYtYMQ": [DF],
    "I3l4XLZ59iw": [DF], "Yb1GCjmw8_8": [DF], "AmUC4m6w1wo": [DF], "LWLadJFI8Pk": [DF], "8nt3edWLgIg": [RISK],
    "JL5OFXeXenA": [RISK], "2ziuPUeewK0": [RISK], "qkHdF8tuKeU": [PRIV], "ugvHCXCOmm4": [RISK], "HjurAWAr_nY": [RISK],
    "ppf3VqpsryU": [AL],
    "wrESBnPYoZU": [RISK], "2Nn0-kAE5c0": [RISK], "uqC4nb7fLpY": [GOV], "FLcrvMfHUJM": [RISK], "S72ZRBSNHZc": [LS, GOV],
    "MPTNHrq_4LU": [GOV], "8zIcP5WlShw": [GOV], "bs5snugP1VA": [AL], "I9aGC6Ui3eE": [AL], "2MBJOuVq380": [AL],
    "XSQ495wpWXs": [AL], "aA7oQ5A3KQc": [LS], "xCUala5j7aQ": [RISK], "jZjmlJPJgug": [PRIV], "8AvIErXFoH8": [AL],
    "INGOC6-LLv0": [LS], "cZLdWtcSE04": [LS], "ZhM29Ds-mBg": [AL], "gP4ZNUHdwp8": [RISK], "w65p_IIp6JY": [AL],
    "eaYIU6YXr3w": [AL], "zATXsGm_xJo": [RISK], "xkQSiS8hpZA": [RISK], "K8p8_VlFHUk": [AL], "mukaRhQTMP8": [RISK, AL],
    "KsZI5oXBC0k": [RISK, AL], "0Uo4soSTe3Q": [AL], "z4M6vN31Vc0": [RISK, AL], "V0aXMTpZTfc": [RISK], "9AAhTLa0dT0": [AL],
    "M2IebCN9Ht4": [ADV], "rGgGOccMEiY": [RISK],
    "ekIL65D0R3o": [PRIV], "gI0wk1CXlsQ": [PRIV], "vsA4w3itxA0": [PRIV], "pT19VwBAqKA": [PRIV], "RWpG0ag6j9c": [PRIV],
    "v5ghK6yUJv4": [LS], "23Mz7qcRz50": [PI, LS], "MaFTqjYjADw": [RISK], "ydnOSMbyyQo": [RISK], "SS9DMr4VkbY": [ADV],
    "CMHL1bPtQdI": [PI, LS], "qyTSOSDEC5M": [PI, LS], "_zfN9wnPvU0": [DF], "VUwBcTgzbtU": [PRIV], "aLx2q-UnH6M": [PI],
    "qpoRO378qRY": [RISK], "17_HcR95YBc": [RISK],
    # --- retags of rule-matched items ---
    "3JH_Zd2mNRs": [RISK, AL], "aX8phGhG8VQ": [AL],
}
REJECT = """9WfZuNceFDM 15q41GjtyZs -DysigzGQvU wrHXA2cSpNU TwNlPI8u1NI fqye4Cw0EF0 34AmKPJNfCg B_qWUVi52yY 9d9pZi7uZQs
uyjSTAOY7yI Wm3squcz7Aw 3vHvOyZ0GbY 8OJnkJqkyio 40lOIZLUACU uo7nAfUZoIM lSM-9RBk3HQ wYSmp-nrJ7M 4lQkQSmA8nA JkUF40kPV4M
C9LDMzMRZv8 duo-tHbSdMk iXqLTJFTUGc imOreIfpzsU ntYeLhST3AU x4yyBWkYSHs NGfGw1tGxUY LE3bGTaAgOE rnDmwW2x16s sXG8CO6aB5w
Hfom0noLFq0 IdK2WKg7kaM yio0XtbpBwQ WS7xmb3UhCU xkNAbgS6b5g iwBOQeFPAwg AKbltBLaFeI 9IMwRIei-Xc Zy7XhkQkUlk""".split()

# --- new categories (jailbreaks / AI-enabled cyber / evals) ---
INCLUDE.update({
    "BwltbhR0JgU": [JB], "1sd26pWhfmg": [CYBER, LS], "B_7RpP90rUk": [CYBER, LS], "v5ghK6yUJv4": [CYBER],
    "INGOC6-LLv0": [CYBER, LS], "S72ZRBSNHZc": [CYBER, GOV], "8rOY3aD1yxY": [CYBER, LS], "sZzcSX7BFVA": [RT, LS],
    "927W6zzvV-c": [LS, RT], "kopoLzvh5jY": [AL], "X50zezLFWWI": [RISK, SE],
})
# --- entertainment / fiction the user does not want (films, parodies, sketches, art pieces) ---
for _v in ["xfMQ7hzyFW4", "O-2tpwW0kmU", "9CO6M2HsoIA", "-TnsQHdI4eo", "-JlxuQ7tPgQ", "cWHTyeQg79A", "5GISvEfdbm4",
           "oxXpB9pSETo", "F4G6GNFz0O8", "IvY-Abd2FfM", "LWLadJFI8Pk", "vW26TB6Rdic", "0p-nNSvB7KA",
           # vendor / product demos and off-topic
           "16BvgmfiYzQ", "pB02u0ntQpM", "PRcE_O1oXIE", "rL9UCGVZEjs", "zQMKfuWZRdA", "pUSWa5hOCtU"]:
    INCLUDE.pop(_v, None)
    REJECT.append(_v)
out = {**INCLUDE, **{v: [] for v in REJECT}}
p = Path(__file__).resolve().parent.parent / "data" / "review_decisions.json"
p.write_text(json.dumps(out, indent=0), encoding="utf-8")
print(f"{len(INCLUDE)} includes, {len(REJECT)} rejects")
