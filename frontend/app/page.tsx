"use client";

import { useState } from "react";

const awsServices = [
  { label: "s3", value: "s3" },
  { label: "dynamodb", value: "dynamodb" },
];

const iamActions = [
  { label: "read", value: "read" },
  { label: "write", value: "write" },
];

const awsServiceTypes = [
  { label: "lambda", value: "lambda" },
  { label: "ec2", value: "ec2" },
];

type PermissionExplanation = {
  permission: string;
  description: string;
};

type SecurityResult = {
  score: number;
  level: string;
};

type SecurityFinding = {
  severity: "low" | "medium" | "high";
  title: string;
  description: string;
};

type ValidationFinding = {
  severity: "low" | "medium" | "high";
  permission: string;
  message: string;
  recommendation: string;
};

type ParsedRequest = {
  aws_service_type: string | null;
  service: string | null;
  action: string | null;
  resource_name: string | null;
};

type GeneratePolicyPayload = {
  service: string;
  action: string;
  aws_service_type: string;
  resource_name: string | null;
};

type GenerationHistoryEntry = GeneratePolicyPayload & {
  id: string;
  generatedAt: string;
};

function getSecurityBadgeClass(level: string) {
  if (level === "Bon") {
    return "badge badge-good";
  }

  if (level === "Moyen") {
    return "badge badge-medium";
  }

  return "badge badge-risk";
}

function formatSecurityLevel(level: string) {
  return level === "Risque eleve" ? "Risque élevé" : level;
}

function getFindingSeverityLabel(severity: SecurityFinding["severity"]) {
  if (severity === "high") {
    return "High";
  }

  if (severity === "medium") {
    return "Medium";
  }

  return "Low";
}

function getRiskLabel(severity: ValidationFinding["severity"]) {
  if (severity === "high") {
    return "Risque élevé";
  }

  if (severity === "medium") {
    return "Risque moyen";
  }

  return "Risque faible";
}

function extractResourceName(text: string) {
  const normalizedText = text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[.,;:!?]/g, " ")
    .replace(/\s+/g, " ");
  const resourceMatch = normalizedText.match(
    /\b(?:bucket|table)\s+(?:nomme\s+|nommee\s+|appele\s+|appelee\s+)?([a-z0-9][a-z0-9._-]*)/,
  );

  const resourceName = resourceMatch?.[1] ?? "";

  if (resourceName === "s3" || resourceName === "dynamodb") {
    return "";
  }

  return resourceName;
}

function buildNlpWarnings(parsedRequest: ParsedRequest) {
  const warnings = [];

  if (!parsedRequest.aws_service_type) {
    warnings.push("Le moteur n'a pas détecté le type de rôle IAM.");
  }

  if (!parsedRequest.service) {
    warnings.push("Le moteur n'a pas détecté le service AWS.");
  }

  if (!parsedRequest.action) {
    warnings.push("Le moteur n'a pas détecté l'action IAM.");
  }

  return warnings;
}

function formatDetectedValue(value: string | null) {
  return value ?? "Non détecté";
}

export default function Home() {
  const [roleName, setRoleName] = useState<string | null>(null);
  const [trustPolicy, setTrustPolicy] = useState<object | null>(null);
  const [policyResult, setPolicyResult] = useState<object | null>(null);
  const [cloudFormationTemplate, setCloudFormationTemplate] = useState<
    string | null
  >(null);
  const [terraformTemplate, setTerraformTemplate] = useState<string | null>(
    null,
  );
  const [warnings, setWarnings] = useState<string[]>([]);
  const [explanations, setExplanations] = useState<PermissionExplanation[]>([]);
  const [securityFindings, setSecurityFindings] = useState<SecurityFinding[]>(
    [],
  );
  const [validationFindings, setValidationFindings] = useState<
    ValidationFinding[]
  >([]);
  const [securityResult, setSecurityResult] = useState<SecurityResult | null>(
    null,
  );
  const [selectedService, setSelectedService] = useState("s3");
  const [selectedAction, setSelectedAction] = useState("read");
  const [awsServiceType, setAwsServiceType] = useState("lambda");
  const [resourceName, setResourceName] = useState("");
  const [userRequestText, setUserRequestText] = useState(
    "Je veux qu'une Lambda lise un bucket S3",
  );
  const [parsedRequest, setParsedRequest] = useState<ParsedRequest | null>(
    null,
  );
  const [parseError, setParseError] = useState<string | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [nlpWarnings, setNlpWarnings] = useState<string[]>([]);
  const [isNlpSuccess, setIsNlpSuccess] = useState(false);
  const [nlpApplyMessage, setNlpApplyMessage] = useState<string | null>(null);
  const [policyActionMessage, setPolicyActionMessage] = useState<string | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationHistory, setGenerationHistory] = useState<
    GenerationHistoryEntry[]
  >([]);

  async function generatePolicyWithPayload(payload: GeneratePolicyPayload) {
    setIsGenerating(true);
    setError(null);
    setPolicyActionMessage(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-policy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          service: payload.service,
          action: payload.action,
          aws_service_type: payload.aws_service_type,
          resource_name: payload.resource_name,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail ?? "Le backend n'a pas pu generer la policy.",
        );
      }

      const data = await response.json();
      setRoleName(data.role_name);
      setTrustPolicy(data.trust_policy);
      setPolicyResult(data.policy);
      setCloudFormationTemplate(data.cloudformation_template);
      setTerraformTemplate(data.terraform_template);
      setWarnings(data.warnings ?? []);
      setExplanations(data.explanations ?? []);
      setValidationFindings(data.validation_findings ?? []);
      setSecurityFindings(data.security_findings ?? []);
      setSecurityResult({
        score: data.security_score,
        level: data.security_level,
      });
      setGenerationHistory((currentHistory) => [
        {
          ...payload,
          id: `${Date.now()}-${currentHistory.length}`,
          generatedAt: new Date().toLocaleTimeString(),
        },
        ...currentHistory,
      ].slice(0, 5));
    } catch (currentError) {
      setRoleName(null);
      setTrustPolicy(null);
      setPolicyResult(null);
      setCloudFormationTemplate(null);
      setTerraformTemplate(null);
      setWarnings([]);
      setExplanations([]);
      setValidationFindings([]);
      setSecurityFindings([]);
      setSecurityResult(null);
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Une erreur inconnue est survenue.",
      );
    } finally {
      setIsGenerating(false);
    }
  }

  async function generatePolicy() {
    await generatePolicyWithPayload({
      service: selectedService,
      action: selectedAction,
      aws_service_type: awsServiceType,
      resource_name: resourceName.trim() || null,
    });
  }

  async function copyPolicyJson() {
    if (!policyResult) {
      return;
    }

    // Le presse-papiers est l'endroit ou l'ordinateur garde ce qui est copie.
    // navigator.clipboard.writeText() sert a copier du texte depuis le navigateur.
    await navigator.clipboard.writeText(JSON.stringify(policyResult, null, 2));
    setPolicyActionMessage("Policy copiée !");
  }

  async function copyCloudFormationTemplate() {
    if (!cloudFormationTemplate) {
      return;
    }

    // On copie le YAML CloudFormation pour pouvoir le reutiliser facilement.
    await navigator.clipboard.writeText(cloudFormationTemplate);
    setPolicyActionMessage("CloudFormation copié !");
  }

  async function copyTerraformTemplate() {
    if (!terraformTemplate) {
      return;
    }

    // On copie le code Terraform pour pouvoir le reutiliser facilement.
    await navigator.clipboard.writeText(terraformTemplate);
    setPolicyActionMessage("Terraform copié !");
  }

  async function parseUserRequest() {
    setIsParsing(true);
    setParseError(null);
    setParsedRequest(null);
    setNlpWarnings([]);
    setIsNlpSuccess(false);
    setNlpApplyMessage(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/parse-request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: userRequestText,
        }),
      });

      if (!response.ok) {
        throw new Error("Le backend n'a pas pu analyser la demande.");
      }

      const data = await response.json();
      setParsedRequest(data);
      setIsNlpSuccess(true);
      setNlpWarnings(buildNlpWarnings(data));
    } catch (currentError) {
      setIsNlpSuccess(false);
      setParseError(
        currentError instanceof Error
          ? currentError.message
          : "Une erreur inconnue est survenue.",
      );
    } finally {
      setIsParsing(false);
    }
  }

  async function generateAutomatically() {
    setIsParsing(true);
    setParseError(null);
    setParsedRequest(null);
    setNlpWarnings([]);
    setIsNlpSuccess(false);
    setNlpApplyMessage(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/parse-request", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: userRequestText,
        }),
      });

      if (!response.ok) {
        throw new Error("Le backend n'a pas pu analyser la demande.");
      }

      const data = await response.json();
      const currentNlpWarnings = buildNlpWarnings(data);
      const extractedResourceName =
        data.resource_name ?? extractResourceName(userRequestText);

      setParsedRequest(data);
      setIsNlpSuccess(true);
      setNlpWarnings(currentNlpWarnings);

      if (data.service) {
        setSelectedService(data.service);
      }

      if (data.action) {
        setSelectedAction(data.action);
      }

      if (data.aws_service_type) {
        setAwsServiceType(data.aws_service_type);
      }

      if (extractedResourceName) {
        setResourceName(extractedResourceName);
      }

      if (currentNlpWarnings.length > 0) {
        return;
      }

      await generatePolicyWithPayload({
        service: data.service,
        action: data.action,
        aws_service_type: data.aws_service_type,
        resource_name: extractedResourceName || resourceName.trim() || null,
      });
    } catch (currentError) {
      setIsNlpSuccess(false);
      setParseError(
        currentError instanceof Error
          ? currentError.message
          : "Une erreur inconnue est survenue.",
      );
    } finally {
      setIsParsing(false);
    }
  }

  function applyParsedRequestToForm() {
    if (!parsedRequest) {
      return;
    }

    if (parsedRequest.service) {
      setSelectedService(parsedRequest.service);
    }

    if (parsedRequest.action) {
      setSelectedAction(parsedRequest.action);
    }

    if (parsedRequest.aws_service_type) {
      setAwsServiceType(parsedRequest.aws_service_type);
    }

    const extractedResourceName =
      parsedRequest.resource_name ?? extractResourceName(userRequestText);

    if (extractedResourceName) {
      setResourceName(extractedResourceName);
    }

    setNlpApplyMessage("Analyse appliquée au formulaire.");
  }

  function reuseHistoryEntry(entry: GenerationHistoryEntry) {
    setSelectedService(entry.service);
    setSelectedAction(entry.action);
    setAwsServiceType(entry.aws_service_type);
    setResourceName(entry.resource_name ?? "");
  }

  function clearHistory() {
    setGenerationHistory([]);
  }

  function downloadPolicyJson() {
    if (!policyResult) {
      return;
    }

    // Un Blob represente ici un petit fichier cree dans le navigateur.
    // URL.createObjectURL() cree une URL temporaire vers ce fichier.
    // Le lien <a> permet de declencher simplement le telechargement.
    const policyBlob = new Blob([JSON.stringify(policyResult, null, 2)], {
      type: "application/json",
    });
    const policyUrl = URL.createObjectURL(policyBlob);
    const downloadLink = document.createElement("a");
    downloadLink.href = policyUrl;
    downloadLink.download = "policy-iam.json";
    downloadLink.click();
    URL.revokeObjectURL(policyUrl);
    setPolicyActionMessage("Téléchargement lancé.");
  }

  return (
    <main className="page">
      <div className="page-shell">
        <section className="card intro-card">
          <p className="eyebrow">Projet IAM</p>
          <h1>Assistant IAM Intelligent</h1>
          <p>
            Génère un rôle IAM pédagogique avec une trust policy, une permission
            policy et un score de sécurité simple.
          </p>
        </section>

        <section className="card parser-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Interpréteur</p>
              <h2>Analyser une demande naturelle</h2>
            </div>
            <span className="muted">Règles simples</span>
          </div>

          <p className="helper-text">
            Le moteur tente de comprendre automatiquement le besoin utilisateur.
            Le moteur reconnaît plusieurs formulations naturelles simples.
            Le moteur NLP tente d'automatiser la génération IAM à partir d'une
            phrase naturelle.
          </p>

          <label className="field">
            <span>Décris ton besoin AWS</span>
            <input
              type="text"
              value={userRequestText}
              onChange={(event) => {
                setUserRequestText(event.target.value);
                setIsNlpSuccess(false);
                setNlpWarnings([]);
                setNlpApplyMessage(null);
              }}
              placeholder="Je veux qu'une Lambda lise un bucket S3"
            />
          </label>

          <div className="parser-actions">
            <button type="button" onClick={parseUserRequest}>
              {isParsing ? "Analyse en cours..." : "Analyser la demande"}
            </button>
            <button type="button" onClick={generateAutomatically}>
              Générer automatiquement
            </button>
          </div>

          {parseError ? <p className="error">{parseError}</p> : null}

          {isNlpSuccess ? (
            <p className="success-message">Analyse NLP réussie</p>
          ) : null}

          {nlpWarnings.length > 0 ? (
            <ul className="warnings">
              {nlpWarnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}

          {parsedRequest ? (
            <div className="json-section">
              <h3>JSON interprété</h3>
              <pre className="policy-output">
                {JSON.stringify(parsedRequest, null, 2)}
              </pre>
            </div>
          ) : null}
        </section>

        {parsedRequest ? (
          <section className="card request-analysis-card">
            <div className="card-header">
              <div>
                <p className="eyebrow">Analyse NLP</p>
                <h2>Analyse de la demande</h2>
              </div>
              <span className="muted">Avant génération</span>
            </div>

            <p>
              L'assistant analyse la phrase utilisateur avant de générer les
              permissions IAM.
              Vous pouvez vérifier l'analyse avant de générer le rôle IAM.
            </p>

            <div className="detected-grid">
              <article className="detected-item">
                <span>Service détecté</span>
                <strong className={parsedRequest.service ? "detected-badge" : "missing-badge"}>
                  {formatDetectedValue(parsedRequest.service)}
                </strong>
              </article>
              <article className="detected-item">
                <span>Action détectée</span>
                <strong className={parsedRequest.action ? "detected-badge" : "missing-badge"}>
                  {formatDetectedValue(parsedRequest.action)}
                </strong>
              </article>
              <article className="detected-item">
                <span>Type AWS détecté</span>
                <strong
                  className={
                    parsedRequest.aws_service_type ? "detected-badge" : "missing-badge"
                  }
                >
                  {formatDetectedValue(parsedRequest.aws_service_type)}
                </strong>
              </article>
              <article className="detected-item">
                <span>Ressource détectée</span>
                <strong
                  className={parsedRequest.resource_name ? "detected-badge" : "missing-badge"}
                >
                  {formatDetectedValue(parsedRequest.resource_name)}
                </strong>
              </article>
            </div>

            {isNlpSuccess ? (
              <div className="analysis-actions">
                <button type="button" onClick={applyParsedRequestToForm}>
                  Utiliser cette analyse
                </button>
                {nlpApplyMessage ? (
                  <p className="success-message">{nlpApplyMessage}</p>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}

        <section className="card generation-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Génération</p>
              <h2>Configurer le rôle IAM</h2>
            </div>
            <span className="muted">Sélecteurs dynamiques</span>
          </div>

          <p className="helper-text">
            Les sélecteurs permettent de construire dynamiquement un rôle IAM.
          </p>

          <div className="selector-grid">
            <label className="field">
              <span>Service AWS</span>
              <select
                value={selectedService}
                onChange={(event) => setSelectedService(event.target.value)}
              >
                {awsServices.map((service) => (
                  <option key={service.value} value={service.value}>
                    {service.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Action</span>
              <select
                value={selectedAction}
                onChange={(event) => setSelectedAction(event.target.value)}
              >
                {iamActions.map((action) => (
                  <option key={action.value} value={action.value}>
                    {action.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Type de rôle IAM</span>
              <select
                value={awsServiceType}
                onChange={(event) => setAwsServiceType(event.target.value)}
              >
                {awsServiceTypes.map((serviceType) => (
                  <option key={serviceType.value} value={serviceType.value}>
                    {serviceType.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="field">
            <span>Nom de la ressource</span>
            <input
              type="text"
              value={resourceName}
              onChange={(event) => setResourceName(event.target.value)}
              placeholder="mon-bucket ou ma-table"
            />
          </label>

          <button
            className="generate-button"
            type="button"
            onClick={generatePolicy}
          >
            {isGenerating ? "Génération en cours..." : "Générer le rôle IAM"}
          </button>

          {error ? <p className="error">{error}</p> : null}
        </section>

        <section className="card history-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Mémoire locale</p>
              <h2>Historique récent</h2>
            </div>
            {generationHistory.length > 0 ? (
              <button type="button" onClick={clearHistory}>
                Vider l'historique
              </button>
            ) : null}
          </div>

          <p>
            L'historique permet de rejouer rapidement des générations IAM
            précédentes.
          </p>

          {generationHistory.length > 0 ? (
            <div className="history-list">
              {generationHistory.map((entry) => (
                <article className="history-item" key={entry.id}>
                  <div>
                    <span className="history-time">{entry.generatedAt}</span>
                    <strong>
                      {entry.aws_service_type} / {entry.service} / {entry.action}
                    </strong>
                    <span className="history-resource">
                      Ressource : {entry.resource_name ?? "Non renseignée"}
                    </span>
                  </div>
                  <button type="button" onClick={() => reuseHistoryEntry(entry)}>
                    Réutiliser
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-history">Aucune génération récente.</p>
          )}
        </section>

        {policyResult ? (
          <>
            <section className="card result-card">
              <div className="card-header">
                <div>
                  <p className="eyebrow">Résultat</p>
                  <h2>Rôle IAM généré</h2>
                </div>
                <div className="policy-actions">
                  <button type="button" onClick={copyPolicyJson}>
                    Copier la policy JSON
                  </button>
                  <button type="button" onClick={downloadPolicyJson}>
                    Télécharger la policy JSON
                  </button>
                </div>
              </div>

              {policyActionMessage ? (
                <p className="success-message">{policyActionMessage}</p>
              ) : null}

              {roleName ? (
                <div className="role-name">
                  <span>Nom du rôle</span>
                  <strong>{roleName}</strong>
                </div>
              ) : null}

              {trustPolicy ? (
                <div className="json-section">
                  <h3>Trust policy</h3>
                  <pre className="policy-output">
                    {JSON.stringify(trustPolicy, null, 2)}
                  </pre>
                </div>
              ) : null}

              <div className="json-section">
                <h3>Permission policy</h3>
                <pre className="policy-output">
                  {JSON.stringify(policyResult, null, 2)}
                </pre>
              </div>

              {warnings.length > 0 ? (
                <ul className="warnings">
                  {warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              ) : null}
            </section>

            {cloudFormationTemplate ? (
              <section className="card template-card">
                <div className="card-header">
                  <div>
                    <p className="eyebrow">Infrastructure as code</p>
                    <h2>Template CloudFormation</h2>
                  </div>
                  <button type="button" onClick={copyCloudFormationTemplate}>
                    Copier CloudFormation
                  </button>
                </div>
                <p>
                  CloudFormation permet de créer des ressources AWS à partir
                  d'un fichier d'infrastructure as code.
                </p>
                <pre className="policy-output">{cloudFormationTemplate}</pre>
              </section>
            ) : null}

            {terraformTemplate ? (
              <section className="card template-card">
                <div className="card-header">
                  <div>
                    <p className="eyebrow">Infrastructure as code</p>
                    <h2>Template Terraform</h2>
                  </div>
                  <button type="button" onClick={copyTerraformTemplate}>
                    Copier Terraform
                  </button>
                </div>
                <p>
                  Terraform permet de gérer l'infrastructure cloud sous forme
                  de code.
                </p>
                <pre className="policy-output">{terraformTemplate}</pre>
              </section>
            ) : null}

            <section className="card iam-validation-card">
              <h2>Validation IAM</h2>
              <p>
                Certaines permissions IAM peuvent représenter un risque
                important.
              </p>
              {validationFindings.length > 0 ? (
                <div className="validation-grid">
                  {validationFindings.map((finding) => (
                    <article
                      className={`validation-item validation-${finding.severity}`}
                      key={`${finding.severity}-${finding.permission}`}
                    >
                      <span>{getRiskLabel(finding.severity)}</span>
                      <strong>{finding.permission}</strong>
                      <p>{finding.message}</p>
                      <small>{finding.recommendation}</small>
                    </article>
                  ))}
                </div>
              ) : (
                <p className="empty-state">
                  Aucune permission critique détectée par les règles de
                  validation actuelles.
                </p>
              )}
            </section>

            {securityResult ? (
              <section className="card security-score">
                <div className="card-header">
                  <div>
                    <p className="eyebrow">Analyse</p>
                    <h2>Score sécurité</h2>
                  </div>
                  <span className={getSecurityBadgeClass(securityResult.level)}>
                    {formatSecurityLevel(securityResult.level)}
                  </span>
                </div>
                <p>
                  Le score de sécurité indique si la policy respecte plutôt
                  bien le principe du Least Privilege.
                </p>
                <div className="score-value">
                  <strong>Score de sécurité : </strong>
                  {securityResult.score}/100
                </div>
                <div className="score-value">
                  <strong>Niveau : </strong>
                  {formatSecurityLevel(securityResult.level)}
                </div>
              </section>
            ) : null}

            <section className="card security-findings">
              <h2>Analyse de sécurité IAM</h2>
              <p>
                Les findings représentent des risques potentiels détectés dans
                la policy IAM.
              </p>
              {securityFindings.length > 0 ? (
                <div className="finding-grid">
                  {securityFindings.map((finding) => (
                    <article
                      className={`finding-card finding-${finding.severity}`}
                      key={`${finding.severity}-${finding.title}`}
                    >
                      <span>{getFindingSeverityLabel(finding.severity)}</span>
                      <h3>{finding.title}</h3>
                      <p>{finding.description}</p>
                    </article>
                  ))}
                </div>
              ) : (
                <p className="empty-state">
                  Aucun risque sensible détecté par les règles simples actuelles.
                </p>
              )}
            </section>

            {explanations.length > 0 ? (
              <section className="card explanations">
                <h2>Explication des permissions</h2>
                <p>
                  Une policy IAM définit ce qu'un service ou un utilisateur a
                  le droit de faire sur AWS.
                </p>
                <ul>
                  {explanations.map((explanation) => (
                    <li key={explanation.permission}>
                      <strong>{explanation.permission}</strong>
                      <span>{explanation.description}</span>
                    </li>
                  ))}
                </ul>
              </section>
            ) : null}

            <section className="card policy-difference">
              <h2>Différence entre trust policy et permission policy</h2>
              <p>
                La trust policy définit <strong>qui</strong> peut utiliser le
                rôle. Par exemple, elle autorise Lambda ou EC2 à assumer ce
                rôle.
              </p>
              <p>
                La permission policy définit <strong>ce que</strong> le rôle
                peut faire sur AWS, comme lire un bucket S3 ou écrire dans une
                table DynamoDB.
              </p>
            </section>
          </>
        ) : null}

        <section className="card next-step">
          <p className="eyebrow">Roadmap</p>
          <h2>Prochaine évolution : validation avancée des permissions IAM</h2>
        </section>
      </div>
    </main>
  );
}
