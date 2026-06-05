import csv
from datetime import datetime, timezone


def load_transactions(path):
    transactions = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(_clean_row(row))
    return transactions


def _clean_row(row):
    def get(key):
        v = row.get(key)
        return v.strip() if isinstance(v, str) and v.strip() != "" else None

    amount_raw = get("amount")
    try:
        amount = float(amount_raw) if amount_raw is not None else None
    except ValueError:
        amount = None

    card_raw = get("card_present")
    if card_raw is None:
        card_present = None
    else:
        card_present = card_raw.lower() in ("true", "1", "yes", "oui")

    return {
        "transaction_id": get("transaction_id"),
        "timestamp":      get("timestamp"),
        "user_id":        get("user_id"),
        "amount":         amount,
        "currency":       get("currency"),
        "merchant":       get("merchant"),
        "country":        get("country"),
        "card_present":   card_present,
    }


def _parse_ts(ts_str):
    if not ts_str:
        return None
    try:
        ts_str = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _geo_risk(prev_cty, cty, minutes):
    if not prev_cty or not cty or prev_cty == cty:
        return False

    # version stabilisée (réduit faux positifs)
    if minutes < 60:
        return True
    if minutes < 180:
        return True
    return False


def detect_fraud(transactions):

    if not transactions:
        return []

    # tri + conservation ordre original
    indexed = []
    for i, tx in enumerate(transactions):
        ts = _parse_ts(tx.get("timestamp"))
        sort_key = ts if ts else datetime.min.replace(tzinfo=timezone.utc)
        indexed.append((i, sort_key, tx))

    indexed.sort(key=lambda x: x[1])

    user_history = {}
    user_times = {}
    user_geo = {}
    seen_ids = set()

    results = {}

    for i, ts, tx in indexed:

        tid = tx.get("transaction_id")
        uid = tx.get("user_id")
        amt = tx.get("amount")
        cty = tx.get("country")
        card = tx.get("card_present")

        score = 0.0
        reasons = []

        # ─────────────────────────
        # NIVEAU 1
        # ─────────────────────────

        if amt is None:
            score += 0.5
            reasons.append("Montant manquant")
        elif amt <= 0:
            score += 0.6
            reasons.append("Montant invalide")

        if not uid:
            score += 0.4
            reasons.append("User manquant")

        if tid and tid in seen_ids:
            score += 0.7
            reasons.append("Doublon transaction")
        if tid:
            seen_ids.add(tid)

        history = user_history.get(uid, [])

        # ─────────────────────────
        # NIVEAU 2 - montant
        # ─────────────────────────

        if uid and amt and amt > 0 and len(history) >= 3:

            mean = sum(history) / len(history)
            var = sum((x - mean) ** 2 for x in history) / len(history)
            std = max(var ** 0.5, 1e-6)

            z = (amt - mean) / std

            if len(history) >= 5:
                if z > 4:
                    score += 0.5
                    reasons.append("Montant extrême")
                elif z > 3:
                    score += 0.3
                    reasons.append("Montant anormal")

            if amt > mean * 4:
                score += 0.25
                reasons.append("Écart montant élevé")

        # ─────────────────────────
        # FRÉQUENCE (corrigée strict passé)
        # ─────────────────────────

        if uid and ts:
            times = user_times.get(uid, [])

            recent = [
                t for t in times
                if 0 < (ts - t).total_seconds() <= 300
            ]

            if len(recent) >= 4:
                score += 0.4
                reasons.append("Fréquence élevée")

        # ─────────────────────────
        # GÉO (stabilisé + bruit réduit)
        # ─────────────────────────

        if uid and ts and cty:
            geo = user_geo.get(uid, [])

            for prev_ts, prev_cty in geo:

                diff = (ts - prev_ts).total_seconds() / 60

                if diff < 0 or diff > 240:
                    continue

                if _geo_risk(prev_cty, cty, diff):
                    score += 0.55
                    reasons.append(f"Géo suspecte {prev_cty}->{cty}")
                    break

        # ─────────────────────────
        # CARD
        # ─────────────────────────

        if card is False and amt and amt > 500:
            score += 0.2
            reasons.append("Sans carte + montant élevé")

        # ─────────────────────────
        # STABILISATION (améliorée)
        # ─────────────────────────

        score = 1 - (1 - score) ** 1.25
        score = min(round(score, 4), 1.0)

        is_suspicious = score >= 0.6

        results[i] = {
            "transaction_id": tid,
            "fraud_score": score,
            "is_suspicious": is_suspicious,
            "reason": " | ".join(reasons) if reasons else "OK"
        }

  
        if uid:
            if amt and amt > 0:
                user_history.setdefault(uid, []).append(amt)

            if ts:
                user_times.setdefault(uid, []).append(ts)
                if cty:
                    user_geo.setdefault(uid, []).append((ts, cty))

    return [results[i] for i in range(len(transactions))]
