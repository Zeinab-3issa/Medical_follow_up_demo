import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Suivi infirmier - Démo",
    layout="wide"
)

TECH_ACTIONS_DONE = [
    "Appel sans réponse",
    "Patient joint",
    "Message vocal laissé",
    "SMS envoyé",
    "Mail envoyé",
    "Relance patient",
    "Relance médecin",
    "Relance pharmacie",
    "Autre"
]

NEXT_ACTIONS = [
    "Recontacter par téléphone", "Recontacter par mail", "Envoyer SMS",
    "Attendre retour patient", "Attendre retour médecin",
    "Transmettre à un autre intervenant", "Dossier clos", "À revoir"
]

RDV_TYPES = [
    "Dermatologue", "Médecin généraliste", "Médecin traitant",
    "Médecin du travail", "Urgences", "Pharmacien",
    "Autre", "Aucun RDV", "Inconnu"
]

INTERVENTION_TYPES = [
    "Exérèse", "Chirurgie", "Cryothérapie / azote", "Biopsie",
    "Curetage", "Greffe", "Ablation", "Laser", "Autre"
]

TREATMENTS = [
    "Crème", "Antibiotique", "Pommade", "Corticoïde",
    "Surveillance", "Pansement / soins locaux", "Aucun", "Autre"
]

LIBELLES_SUIVI = [
    "Suivi_Technique",
    "Rien_Technique",
    "Non_Intervention",
    "Intervention_sans_Anapath",
    "Intervention_Anapath_inconnu",
    "Intervention_Anapath_avec_diag_benin",
    "Intervention_Anapath_avec_diag_malin",
]


def create_demo_data():
    return pd.DataFrame([
        {
            "case_id": "DOSSIER-001",
            "annotation_status": "À traiter",
            "dossier_status": "Rouge",
            "dossier_source": "Pharmacie",
            "followup_category": "Suivi technique",
            "action_done": "",
            "contact_attempt_count": 0,
            "next_action": "",
            "medical_info_obtained": False,
            "rdv_type": "",
            "doctor_name": "",
            "doctor_phone": "",
            "intervention_done": "",
            "intervention_type": "",
            "anapath_done": "",
            "anapath_result": "",
            "diagnostic_present": "",
            "diagnostic_type": "",
            "diagnostic_precise": "",
            "treatment_done": "",
            "treatment_type": "",
            "cr_available": "",
            "cr_file_name": "",
            "libelle_suivi_calcule": "",
            "libelle_suivi_manuel": "",
            "libelle_suivi": "",
            "nurse_notes": "",
            "annotated_by": "",
            "annotated_at": "",
        },
        {
            "case_id": "DOSSIER-002",
            "annotation_status": "À traiter",
            "dossier_status": "Orange",
            "dossier_source": "Entreprise",
            "followup_category": "Information médicale obtenue",
            "action_done": "",
            "contact_attempt_count": 1,
            "next_action": "",
            "medical_info_obtained": False,
            "rdv_type": "",
            "doctor_name": "",
            "doctor_phone": "",
            "intervention_done": "",
            "intervention_type": "",
            "anapath_done": "",
            "anapath_result": "",
            "diagnostic_present": "",
            "diagnostic_type": "",
            "diagnostic_precise": "",
            "treatment_done": "",
            "treatment_type": "",
            "cr_available": "",
            "cr_file_name": "",
            "libelle_suivi_calcule": "",
            "libelle_suivi_manuel": "",
            "libelle_suivi": "",
            "nurse_notes": "",
            "annotated_by": "",
            "annotated_at": "",
        },
    ])


def safe_get(row, col, default=""):
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return val


def compute_libelle_suivi(values):
    category = values.get("followup_category", "")
    attempts = int(values.get("contact_attempt_count") or 0)
    next_action = values.get("next_action", "")

    if category == "Suivi technique":
        if attempts >= 6 or next_action == "Dossier clos":
            return "Rien_Technique"
        return "Suivi_Technique"

    if category != "Information médicale obtenue":
        return "Suivi_Technique"

    intervention = values.get("intervention_done", "")

    if intervention == "Non":
        return "Non_Intervention"

    if intervention == "Inconnu":
        return "Suivi_Technique"

    anapath = values.get("anapath_done", "")

    if anapath == "Non":
        return "Intervention_sans_Anapath"

    if anapath == "Inconnu":
        return "Intervention_Anapath_inconnu"

    result = values.get("anapath_result", "")

    if result == "Bénin":
        return "Intervention_Anapath_avec_diag_benin"

    if result == "Malin":
        return "Intervention_Anapath_avec_diag_malin"

    return "Intervention_Anapath_inconnu"


if "df" not in st.session_state:
    st.session_state.df = create_demo_data()
    st.session_state.current_idx = 0

df = st.session_state.df

st.title("SkinApp Expertise — Suivi infirmier")
st.caption(
    "Démo fonctionnelle de l’interface de suivi médical des dossiers patients rouges et oranges."
)

with st.sidebar:
    st.header("📁 File de suivi")

    view_mode = st.selectbox(
        "Vue",
        ["À suivre", "En cours", "Tous les dossiers"]
    )

    status_filter = st.selectbox(
        "Filtrer par statut",
        ["Tous", "Rouge", "Orange"]
    )

    source_filter = st.selectbox(
        "Filtrer par source",
        ["Toutes", "Pharmacie", "Entreprise"]
    )

    side_view = df.copy()

    if view_mode == "À suivre":
        side_view = side_view[side_view["annotation_status"] != "Validé"]
    elif view_mode == "En cours":
        side_view = side_view[side_view["annotation_status"] == "En cours"]

    if status_filter != "Tous":
        side_view = side_view[side_view["dossier_status"] == status_filter]

    if source_filter != "Toutes":
        side_view = side_view[side_view["dossier_source"] == source_filter]

    ids = side_view.index.tolist()

    if not ids:
        st.success("Aucun dossier dans cette vue.")
        st.stop()

    selected = st.selectbox(
        "Dossier",
        ids,
        format_func=lambda i: (
            f"{df.loc[i, 'case_id']} · "
            f"Statut : {df.loc[i, 'dossier_status']} · "
            f"Source : {df.loc[i, 'dossier_source']} · "
            f"{df.loc[i, 'annotation_status']}"
        )
    )

    st.session_state.current_idx = selected

idx = st.session_state.current_idx
row = df.loc[idx]

left, right = st.columns([0.4, 0.6], gap="large")

with left:
    st.subheader("👤 Dossier expertisé")

    st.markdown(
        """
        <div style='height:220px;border-radius:18px;background:#1f2937;
        display:flex;align-items:center;justify-content:center;
        border:1px solid #374151;'>
            <div style='text-align:center;color:#d1d5db;font-size:42px;'>
                📷<br>
                <span style='font-size:14px;'>
                    Galerie d’images SkinApp<br>
                    Données patient et télé-expertises réalisées
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.info("**Statut :** rouge / orange")
    st.info("**Source :** pharmacie / entreprise")

    st.write("**Identité patient :** Nom / Prénom")
    st.write("**Téléphone :** 06 00 00 00 00")
    st.write("**Âge du patient :** 65 ans")
    st.write("**Dossier médical :** patient_id / medicalfile_id")
    st.write("**Statut annotation :**", safe_get(row, "annotation_status", "À traiter"))

    st.info(
        "La partie ci-dessus mime les données réelles issues de SkinApp Expertise : "
        "galerie d’images, données patient, télé-expertise, statut du dossier rouge/orange "
        "et source du dossier pharmacie/entreprise."
    )

with right:
    st.subheader("☎️ Suivi infirmier")

    st.markdown("#### 1) Contact / suivi")

    c1, c2, c3 = st.columns(3)

    with c1:
        followup_category = st.radio(
            "Situation du suivi",
            [
                "Suivi technique",
                "Information médicale obtenue",
            ],
            index=0,
        )

    with c2:
        action_done = st.selectbox(
            "Action faite",
            [""] + TECH_ACTIONS_DONE
        )

    with c3:
        contact_attempt_count = st.number_input(
            "Tentatives",
            min_value=0,
            max_value=6,
            value=int(safe_get(row, "contact_attempt_count", 0) or 0),
            step=1,
        )

    next_action = st.selectbox(
        "Action à faire",
        [""] + NEXT_ACTIONS
    )

    values = {
        "followup_category": followup_category,
        "action_done": action_done,
        "contact_attempt_count": contact_attempt_count,
        "next_action": next_action,
        "medical_info_obtained": False,
    }

    if followup_category == "Information médicale obtenue":
        st.markdown("#### 2) Information médicale recueillie")

        rdv_type = st.selectbox("RDV médical", RDV_TYPES)

        doctor_name = st.text_input(
            "Nom du médecin, dermatologue ou centre médical",
            value=str(safe_get(row, "doctor_name", "")),
            placeholder="Ex. Dr Dermato, Centre dermatologique, hôpital, etc..."
        )

        doctor_phone = st.text_input(
            "Téléphone du médecin ou du centre",
            value=str(safe_get(row, "doctor_phone", "")),
            placeholder="Ex. 01 23 45 67 89"
        )

        intervention_done = st.radio(
            "Intervention réalisée ?",
            ["Oui", "Non", "Inconnu"],
            horizontal=True,
        )

        values.update({
            "medical_info_obtained": True,
            "rdv_type": rdv_type,
            "doctor_name": doctor_name,
            "doctor_phone": doctor_phone,
            "intervention_done": intervention_done,
        })

        diagnostic_present = st.radio(
            "Diagnostic disponible ?",
            ["Oui", "Non", "Inconnu"],
            horizontal=True,
        )

        values["diagnostic_present"] = diagnostic_present

        if diagnostic_present == "Oui":
            dc1, dc2 = st.columns(2)

            with dc1:
                diagnostic_type = st.selectbox(
                    "Nature du diagnostic",
                    ["", "Bénin", "Malin", "Inconnu"]
                )

            with dc2:
                diagnostic_precise = st.text_input(
                    "Diagnostic précis"
                )

            values.update({
                "diagnostic_type": diagnostic_type,
                "diagnostic_precise": diagnostic_precise,
            })

        if intervention_done == "Non":
            treatment_done = st.radio(
                "Traitement ?",
                ["Oui", "Non", "Inconnu"],
                horizontal=True,
            )

            values["treatment_done"] = treatment_done

            if treatment_done == "Oui":
                values["treatment_type"] = st.selectbox(
                    "Type de traitement",
                    TREATMENTS
                )

        elif intervention_done == "Oui":
            intervention_type = st.selectbox(
                "Type d’intervention",
                INTERVENTION_TYPES
            )

            anapath_done = st.radio(
                "Anapath réalisée ?",
                ["Oui", "Non", "Inconnu"],
                horizontal=True,
            )

            values.update({
                "intervention_type": intervention_type,
                "anapath_done": anapath_done,
            })

            if anapath_done == "Oui":
                anapath_result = st.radio(
                    "Résultat anapath",
                    ["Bénin", "Malin", "Inconnu"],
                    horizontal=True,
                )

                values["anapath_result"] = anapath_result

                cr_available = st.radio(
                    "Compte-rendu disponible ?",
                    ["Oui", "Non"],
                    horizontal=True,
                )

                values["cr_available"] = cr_available

                if cr_available == "Oui":
                    st.markdown("##### Dépôt du compte-rendu")

                    uploaded_cr = st.file_uploader(
                        "Déposez ici un document Word ou PDF pour simuler l’ajout d’un compte-rendu.",
                        type=["pdf", "doc", "docx"],
                        help="Démo uniquement : le fichier permet de tester le parcours utilisateur."
                    )

                    if uploaded_cr is not None:
                        st.success(
                            f"Document chargé pour la démonstration : {uploaded_cr.name}"
                        )
                        values["cr_file_name"] = uploaded_cr.name

    libelle_suivi_calcule = compute_libelle_suivi(values)

    st.divider()
    st.markdown("#### 3) Validation")

    st.success(
        f"Libellé standard calculé automatiquement : {libelle_suivi_calcule}"
    )

    override = st.checkbox(
        "Corriger manuellement le libellé standard"
    )

    libelle_suivi_manuel = ""

    if override:
        libelle_suivi_manuel = st.selectbox(
            "Libellé standard manuel",
            LIBELLES_SUIVI,
            index=LIBELLES_SUIVI.index(libelle_suivi_calcule),
        )

    nurse_notes = st.text_area(
        "Notes infirmières",
        value=str(safe_get(row, "nurse_notes", "")),
        height=90,
        placeholder="Saisir ici les informations utiles au suivi."
    )

    b1, b2, b3 = st.columns(3)

    if b1.button("💾 Enregistrer", type="primary", use_container_width=True):
        final_libelle = libelle_suivi_manuel or libelle_suivi_calcule

        for key, val in values.items():
            df.at[idx, key] = val

        df.at[idx, "libelle_suivi_calcule"] = libelle_suivi_calcule
        df.at[idx, "libelle_suivi_manuel"] = libelle_suivi_manuel
        df.at[idx, "libelle_suivi"] = final_libelle
        df.at[idx, "nurse_notes"] = nurse_notes
        df.at[idx, "annotation_status"] = "En cours"
        df.at[idx, "annotated_by"] = "infirmiere_demo"
        df.at[idx, "annotated_at"] = datetime.now().isoformat(timespec="seconds")

        st.session_state.df = df
        st.toast("Suivi enregistré")
        st.rerun()

    if b2.button("✅ Valider et suivant", use_container_width=True):
        final_libelle = libelle_suivi_manuel or libelle_suivi_calcule

        for key, val in values.items():
            df.at[idx, key] = val

        df.at[idx, "libelle_suivi_calcule"] = libelle_suivi_calcule
        df.at[idx, "libelle_suivi_manuel"] = libelle_suivi_manuel
        df.at[idx, "libelle_suivi"] = final_libelle
        df.at[idx, "nurse_notes"] = nurse_notes
        df.at[idx, "annotation_status"] = "Validé"
        df.at[idx, "annotated_by"] = "infirmiere_demo"
        df.at[idx, "annotated_at"] = datetime.now().isoformat(timespec="seconds")

        st.session_state.df = df
        st.toast("Dossier validé")
        st.rerun()

    if b3.button("⏭️ Passer", use_container_width=True):
        next_idx = min(idx + 1, len(df) - 1)
        st.session_state.current_idx = next_idx
        st.rerun()

    st.divider()

    export_df = df.copy()
    csv = export_df.to_csv(sep=";", index=False).encode("utf-8")

    st.download_button(
        "⬇️ Export CSV de suivi",
        data=csv,
        file_name="suivi_infirmier_demo.csv",
        mime="text/csv",
    )
