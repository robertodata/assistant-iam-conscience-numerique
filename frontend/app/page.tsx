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

const userModes = [
  { label: "Débutant", value: "beginner" },
  { label: "Expert", value: "expert" },
];

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const IAM_ACTION_DETAILS: Record<
  string,
  { description: string; risk: "low" | "medium" | "high" }
> = {
  "s3:GetObject": {
    description: "Permet de lire des objets dans un bucket S3.",
    risk: "low",
  },
  "s3:ListBucket": {
    description: "Permet de lister le contenu d'un bucket S3.",
    risk: "low",
  },
  "s3:PutObject": {
    description: "Permet d'ajouter ou modifier des objets dans un bucket S3.",
    risk: "medium",
  },
  "s3:DeleteObject": {
    description: "Permet de supprimer des objets dans un bucket S3.",
    risk: "high",
  },
  "dynamodb:GetItem": {
    description: "Permet de lire un élément précis dans une table DynamoDB.",
    risk: "low",
  },
  "dynamodb:Query": {
    description: "Permet de rechercher des éléments dans une table DynamoDB.",
    risk: "low",
  },
  "dynamodb:Scan": {
    description: "Permet de parcourir une table DynamoDB plus largement.",
    risk: "medium",
  },
  "dynamodb:PutItem": {
    description: "Permet d'écrire un élément dans une table DynamoDB.",
    risk: "medium",
  },
  "dynamodb:UpdateItem": {
    description: "Permet de modifier un élément dans une table DynamoDB.",
    risk: "medium",
  },
  "dynamodb:DeleteItem": {
    description: "Permet de supprimer un élément dans une table DynamoDB.",
    risk: "high",
  },
  "lambda:InvokeFunction": {
    description: "Permet d'invoquer une fonction Lambda.",
    risk: "medium",
  },
  "lambda:CreateFunction": {
    description: "Permet de créer une fonction Lambda.",
    risk: "high",
  },
  "lambda:UpdateFunctionCode": {
    description: "Permet de modifier le code d'une fonction Lambda.",
    risk: "high",
  },
  "ec2:DescribeInstances": {
    description: "Permet de consulter les informations des instances EC2.",
    risk: "low",
  },
  "ec2:StartInstances": {
    description: "Permet de démarrer des instances EC2.",
    risk: "medium",
  },
  "ec2:StopInstances": {
    description: "Permet d'arrêter des instances EC2.",
    risk: "medium",
  },
  "ecr:GetAuthorizationToken": {
    description: "Permet de s'authentifier auprès d'Amazon ECR.",
    risk: "medium",
  },
  "ecr:BatchCheckLayerAvailability": {
    description: "Permet de vérifier les couches déjà présentes dans ECR.",
    risk: "low",
  },
  "ecr:InitiateLayerUpload": {
    description: "Permet de démarrer l'upload d'une couche d'image Docker.",
    risk: "medium",
  },
  "ecr:UploadLayerPart": {
    description: "Permet d'envoyer une partie d'une image Docker vers ECR.",
    risk: "medium",
  },
  "ecr:CompleteLayerUpload": {
    description: "Permet de finaliser l'upload d'une couche d'image Docker.",
    risk: "medium",
  },
  "ecr:PutImage": {
    description: "Permet de pousser une image Docker dans un repository ECR.",
    risk: "medium",
  },
  "ecr:BatchGetImage": {
    description: "Permet de récupérer les métadonnées d'une image ECR.",
    risk: "low",
  },
  "ecr:GetDownloadUrlForLayer": {
    description: "Permet de télécharger les couches d'une image ECR.",
    risk: "low",
  },
  "cloudwatch:GetMetricData": {
    description: "Permet de lire des métriques CloudWatch.",
    risk: "low",
  },
  "cloudwatch:ListMetrics": {
    description: "Permet de lister les métriques CloudWatch disponibles.",
    risk: "low",
  },
  "logs:CreateLogGroup": {
    description: "Permet de créer un groupe de logs CloudWatch.",
    risk: "medium",
  },
  "logs:CreateLogStream": {
    description: "Permet de créer un flux de logs CloudWatch.",
    risk: "medium",
  },
  "logs:PutLogEvents": {
    description: "Permet d'écrire des événements dans CloudWatch Logs.",
    risk: "medium",
  },
  "aws-portal:ViewBilling": {
    description: "Permet de consulter les informations de facturation AWS.",
    risk: "medium",
  },
  "ce:GetCostAndUsage": {
    description: "Permet de consulter les coûts et usages AWS.",
    risk: "medium",
  },
  "aws-portal:ModifyBilling": {
    description: "Permet de modifier des informations de facturation AWS.",
    risk: "high",
  },
};

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

type PolicyStatement = {
  Action: string[];
  Resource: string | string[];
};

type IamPolicy = {
  Statement: PolicyStatement[];
};

type DetectedPermission = {
  service: string;
  action: string;
  resource_name?: string;
};

type ParsedRequest = {
  aws_service_type: string | null;
  service: string | null;
  action: string | null;
  permissions?: DetectedPermission[];
  resource_name: string | null;
};

type GeneratePolicyPayload = {
  service: string;
  action: string;
  permissions?: DetectedPermission[];
  aws_service_type: string;
  resource_name: string | null;
  mode: string;
};

type GenerationHistoryEntry = GeneratePolicyPayload & {
  id: string;
  generatedAt: string;
};

type IamAnalysisResult = {
  request: string;
  services: string[];
  intents: string[];
  actions: string[];
  resource_name: string | null;
  resource_arn: string | string[] | null;
  risk_level: "low" | "medium" | "high";
  recommendations: string[];
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

function getAnalysisRiskLabel(riskLevel: IamAnalysisResult["risk_level"]) {
  if (riskLevel === "high") {
    return "Risque élevé";
  }

  if (riskLevel === "medium") {
    return "Risque moyen";
  }

  return "Risque faible";
}

function getAnalysisRiskBadgeClass(riskLevel: IamAnalysisResult["risk_level"]) {
  if (riskLevel === "high") {
    return "badge badge-risk";
  }

  if (riskLevel === "medium") {
    return "badge badge-medium";
  }

  return "badge badge-good";
}

function getActionDescription(action: string) {
  return (
    IAM_ACTION_DETAILS[action]?.description ??
    "Permission IAM proposée par le catalogue AWS."
  );
}

function getActionRisk(action: string) {
  return IAM_ACTION_DETAILS[action]?.risk ?? "medium";
}

function getActionRiskLabel(risk: "low" | "medium" | "high") {
  if (risk === "high") {
    return "high";
  }

  if (risk === "medium") {
    return "medium";
  }

  return "low";
}

function buildInteractivePolicy(actions: string[], resource: string | string[] = "*") {
  return {
    Version: "2012-10-17",
    Statement: [
      {
        Effect: "Allow",
        Action: actions,
        Resource: resource,
      },
    ],
  };
}

function buildTerraformFromActions(actions: string[], resource: string | string[]) {
  const policyJson = JSON.stringify(buildInteractivePolicy(actions, resource), null, 2);

  return `resource "aws_iam_policy" "generated_policy" {
  name        = "assistant-iam-generated-policy"
  description = "Policy IAM générée depuis l'analyse interactive"

  policy = jsonencode(${policyJson})
}
`;
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

function formatUserMode(mode: string) {
  return mode === "expert" ? "Expert" : "Débutant";
}

function formatAwsServiceType(serviceType: string | undefined) {
  if (serviceType === "ec2") {
    return "EC2";
  }

  return "Lambda";
}

function formatResourceValue(resource: string | string[]) {
  if (Array.isArray(resource)) {
    return resource.join(", ");
  }

  return resource;
}

function hasWildcardResource(policy: IamPolicy | null) {
  if (!policy) {
    return false;
  }

  return policy.Statement.some((statement) => {
    if (Array.isArray(statement.Resource)) {
      return statement.Resource.includes("*");
    }

    return statement.Resource === "*";
  });
}

function replaceWildcardResources(policy: IamPolicy, resourceArn: string): IamPolicy {
  return {
    ...policy,
    Statement: policy.Statement.map((statement) => ({
      ...statement,
      Resource: Array.isArray(statement.Resource)
        ? statement.Resource.map((resource) =>
            resource === "*" ? resourceArn : resource,
          )
        : statement.Resource === "*"
          ? resourceArn
          : statement.Resource,
    })),
  };
}

function analyzePolicySecurity(policy: IamPolicy): SecurityFinding[] {
  const findings: SecurityFinding[] = [];

  policy.Statement.forEach((statement) => {
    const resources = Array.isArray(statement.Resource)
      ? statement.Resource
      : [statement.Resource];

    if (resources.includes("*")) {
      findings.push({
        severity: "medium",
        title: "Resource trop large",
        description:
          "Resource '*' applique la permission à toutes les ressources compatibles.",
      });
    }

    statement.Action.forEach((action) => {
      if (action.includes("*")) {
        findings.push({
          severity: "high",
          title: "Wildcard Action détecté",
          description:
            "Action '*' donne tous les droits possibles pour le périmètre cible.",
        });
      }

      if (action.includes("Delete")) {
        findings.push({
          severity: "medium",
          title: "Permission Delete détectée",
          description: `La permission ${action} peut supprimer des données ou des ressources.`,
        });
      }
    });
  });

  return findings;
}

function calculateSecurityResultFromFindings(
  findings: SecurityFinding[],
): SecurityResult {
  const score = findings.reduce((currentScore, finding) => {
    if (finding.severity === "high") {
      return currentScore - 30;
    }

    if (finding.severity === "medium") {
      return currentScore - 15;
    }

    return currentScore - 5;
  }, 100);
  const safeScore = Math.max(score, 0);

  if (safeScore >= 80) {
    return { score: safeScore, level: "Bon" };
  }

  if (safeScore >= 50) {
    return { score: safeScore, level: "Moyen" };
  }

  return { score: safeScore, level: "Risque eleve" };
}

export default function Home() {
  const [roleName, setRoleName] = useState<string | null>(null);
  const [trustPolicy, setTrustPolicy] = useState<object | null>(null);
  const [policyResult, setPolicyResult] = useState<IamPolicy | null>(null);
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
  const [userMode, setUserMode] = useState("beginner");
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
  const [lastGeneratedPayload, setLastGeneratedPayload] =
    useState<GeneratePolicyPayload | null>(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);
  const [isAskingAi, setIsAskingAi] = useState(false);
  const [resourceArn, setResourceArn] = useState("");
  const [resourceArnMessage, setResourceArnMessage] = useState<string | null>(
    null,
  );
  const [resourceArnError, setResourceArnError] = useState<string | null>(null);
  const [iamAnalysisText, setIamAnalysisText] = useState(
    "Je veux qu'une Lambda lise un bucket S3 et écrive dans DynamoDB",
  );
  const [iamAnalysisResult, setIamAnalysisResult] =
    useState<IamAnalysisResult | null>(null);
  const [iamAnalysisError, setIamAnalysisError] = useState<string | null>(null);
  const [isAnalyzingIam, setIsAnalyzingIam] = useState(false);
  const [selectedIamActions, setSelectedIamActions] = useState<string[]>([]);
  const [interactivePolicyMessage, setInteractivePolicyMessage] = useState<
    string | null
  >(null);

  async function generatePolicyWithPayload(payload: GeneratePolicyPayload) {
    setIsGenerating(true);
    setError(null);
    setPolicyActionMessage(null);
    setResourceArnMessage(null);
    setResourceArnError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/generate-policy`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          service: payload.service,
          action: payload.action,
          permissions: payload.permissions,
          aws_service_type: payload.aws_service_type,
          resource_name: payload.resource_name,
          mode: payload.mode,
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
      setLastGeneratedPayload(payload);
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
      setLastGeneratedPayload(null);
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
      mode: userMode,
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
      const response = await fetch(`${API_BASE_URL}/parse-request`, {
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

  async function askIamAssistant() {
    const trimmedPrompt = aiPrompt.trim();

    if (!trimmedPrompt) {
      setAiError("Écris une question IAM avant de demander à l'IA.");
      setAiResponse(null);
      return;
    }

    setIsAskingAi(true);
    setAiError(null);
    setAiResponse(null);

    try {
      const response = await fetch(`${API_BASE_URL}/ai/explain`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: trimmedPrompt,
        }),
      });

      if (!response.ok) {
        throw new Error("L'assistant IA n'a pas pu répondre.");
      }

      const data = await response.json();
      setAiResponse(data.explanation ?? "Aucune réponse IA disponible.");
    } catch (currentError) {
      setAiError(
        currentError instanceof Error
          ? currentError.message
          : "Une erreur inconnue est survenue avec l'assistant IA.",
      );
    } finally {
      setIsAskingAi(false);
    }
  }

  async function analyzeIamRequest() {
    const trimmedRequest = iamAnalysisText.trim();

    if (!trimmedRequest) {
      setIamAnalysisError("Écris une demande IAM avant de lancer l'analyse.");
      setIamAnalysisResult(null);
      return;
    }

    setIsAnalyzingIam(true);
    setIamAnalysisError(null);
    setIamAnalysisResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/iam/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          request: trimmedRequest,
        }),
      });

      if (!response.ok) {
        throw new Error("Le backend n'a pas pu analyser cette demande IAM.");
      }

      const data = await response.json();
      setIamAnalysisResult(data);
      setSelectedIamActions(data.actions ?? []);
      setInteractivePolicyMessage(null);
    } catch (currentError) {
      setIamAnalysisError(
        currentError instanceof Error
          ? currentError.message
          : "Une erreur inconnue est survenue pendant l'analyse IAM.",
      );
    } finally {
      setIsAnalyzingIam(false);
    }
  }

  function toggleIamAction(action: string) {
    setSelectedIamActions((currentActions) =>
      currentActions.includes(action)
        ? currentActions.filter((currentAction) => currentAction !== action)
        : [...currentActions, action],
    );
    setInteractivePolicyMessage(null);
  }

  async function copyInteractivePolicyJson() {
    await navigator.clipboard.writeText(
      JSON.stringify(
        buildInteractivePolicy(selectedIamActions, generatedArnValue),
        null,
        2,
      ),
    );
    setInteractivePolicyMessage("Policy JSON copiée.");
  }

  function exportInteractiveTerraform() {
    downloadGeneratedFile(
      buildTerraformFromActions(selectedIamActions, generatedArnValue),
      "interactive-iam-policy.tf",
      "text/plain",
    );
    setInteractivePolicyMessage("Export Terraform lancé.");
  }

  async function copyGeneratedArn() {
    if (!iamAnalysisResult?.resource_arn) {
      return;
    }

    await navigator.clipboard.writeText(
      Array.isArray(iamAnalysisResult.resource_arn)
        ? iamAnalysisResult.resource_arn.join("\n")
        : iamAnalysisResult.resource_arn,
    );
    setInteractivePolicyMessage("ARN copié.");
  }


  async function generateAutomatically() {
    setIsParsing(true);
    setParseError(null);
    setParsedRequest(null);
    setNlpWarnings([]);
    setIsNlpSuccess(false);
    setNlpApplyMessage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/parse-request`, {
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
        permissions: data.permissions,
        aws_service_type: data.aws_service_type,
        resource_name: extractedResourceName || resourceName.trim() || null,
        mode: userMode,
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
    setUserMode(entry.mode);
  }

  function clearHistory() {
    setGenerationHistory([]);
  }

  function applyResourceArn() {
    const trimmedArn = resourceArn.trim();

    if (!trimmedArn) {
      setResourceArnError("Renseigne un ARN avant de l'appliquer.");
      setResourceArnMessage(null);
      return;
    }

    if (!trimmedArn.startsWith("arn:aws:")) {
      setResourceArnError("L'ARN doit commencer par arn:aws:");
      setResourceArnMessage(null);
      return;
    }

    if (!policyResult || !hasWildcardResource(policyResult)) {
      setResourceArnError("Génère d'abord une policy contenant Resource '*'.");
      setResourceArnMessage(null);
      return;
    }

    const updatedPolicy = replaceWildcardResources(policyResult, trimmedArn);
    const updatedFindings = analyzePolicySecurity(updatedPolicy);

    setPolicyResult(updatedPolicy);
    setSecurityFindings(updatedFindings);
    setSecurityResult(calculateSecurityResultFromFindings(updatedFindings));
    setWarnings((currentWarnings) =>
      currentWarnings.filter(
        (warning) =>
          !warning.includes("Resource '*'") && !warning.includes("trop large"),
      ),
    );
    setResourceArnError(null);
    setResourceArnMessage("ARN appliqué à la permission policy.");
  }

  function downloadGeneratedFile(
    content: string,
    fileName: string,
    mimeType: string,
  ) {
    // Un Blob represente ici un petit fichier cree dans le navigateur.
    // URL.createObjectURL() cree une URL temporaire vers ce fichier.
    // Le lien <a> permet de declencher simplement le telechargement.
    const generatedBlob = new Blob([content], {
      type: mimeType,
    });
    const generatedUrl = URL.createObjectURL(generatedBlob);
    const downloadLink = document.createElement("a");
    downloadLink.href = generatedUrl;
    downloadLink.download = fileName;
    downloadLink.click();
    URL.revokeObjectURL(generatedUrl);
    setPolicyActionMessage("Téléchargement lancé.");
  }

  function downloadPolicyJson() {
    if (!policyResult) {
      return;
    }

    downloadGeneratedFile(
      JSON.stringify(policyResult, null, 2),
      "policy-iam.json",
      "application/json",
    );
  }

  function downloadPermissionPolicyJson() {
    if (!policyResult) {
      return;
    }

    downloadGeneratedFile(
      JSON.stringify(policyResult, null, 2),
      "permission-policy.json",
      "application/json",
    );
  }

  function downloadTrustPolicyJson() {
    if (!trustPolicy) {
      return;
    }

    downloadGeneratedFile(
      JSON.stringify(trustPolicy, null, 2),
      "trust-policy.json",
      "application/json",
    );
  }

  function downloadCloudFormationYaml() {
    if (!cloudFormationTemplate) {
      return;
    }

    downloadGeneratedFile(
      cloudFormationTemplate,
      "cloudformation-template.yaml",
      "application/x-yaml",
    );
  }

  function downloadTerraformTf() {
    if (!terraformTemplate) {
      return;
    }

    downloadGeneratedFile(
      terraformTemplate,
      "terraform-template.tf",
      "text/plain",
    );
  }

  const policyStatements = policyResult?.Statement ?? [];
  const permissionCount = policyStatements.reduce(
    (total, statement) => total + statement.Action.length,
    0,
  );
  const exportNames = [
    policyResult ? "JSON" : null,
    trustPolicy ? "Trust Policy JSON" : null,
    cloudFormationTemplate ? "CloudFormation" : null,
    terraformTemplate ? "Terraform" : null,
  ].filter(Boolean);
  const isNlpResourceMissing = parsedRequest ? !parsedRequest.resource_name : false;
  const isPolicyResourceWildcard = hasWildcardResource(policyResult);
  const shouldShowResourceGuidance =
    isNlpResourceMissing || isPolicyResourceWildcard;
  const generatedArnValue = iamAnalysisResult?.resource_arn ?? "*";
  const interactivePolicy = buildInteractivePolicy(
    selectedIamActions,
    generatedArnValue,
  );

  return (
    <main className="page">
      <div className="page-shell">
        <section className="card intro-card">
          <h1>Assistant IAM Intelligent</h1>
          <p>
            Décrivez votre besoin AWS en langage naturel. L'assistant identifie
            les services, propose les permissions IAM adaptées et génère une
            policy plus sûre.
          </p>
        </section>

        <section className="card iam-smart-analysis-card">
          <div className="card-header">
            <div>
              <h2>Analyse IAM intelligente</h2>
            </div>
            <span className="muted">Permissions suggérées</span>
          </div>

          <p className="helper-text">
            Saisissez un besoin métier : l'assistant propose les permissions,
            les risques, les recommandations et l'ARN de ressource quand il le
            détecte.
          </p>

          <label className="field">
            <span>Demande IAM</span>
            <textarea
              value={iamAnalysisText}
              onChange={(event) => {
                setIamAnalysisText(event.target.value);
                setIamAnalysisError(null);
              }}
              placeholder="Ex: Je veux qu’une Lambda lise un bucket S3 et écrive dans DynamoDB"
              rows={5}
            />
          </label>

          <button
            type="button"
            onClick={analyzeIamRequest}
            disabled={isAnalyzingIam}
          >
            {isAnalyzingIam ? "Analyse en cours..." : "Analyser la demande"}
          </button>

          {iamAnalysisError ? <p className="error">{iamAnalysisError}</p> : null}

          {iamAnalysisResult ? (
            <div className="iam-analysis-result">
              <div className="analysis-summary-row">
                <div>
                  <span>Niveau de risque</span>
                  <strong
                    className={getAnalysisRiskBadgeClass(
                      iamAnalysisResult.risk_level,
                    )}
                  >
                    {getAnalysisRiskLabel(iamAnalysisResult.risk_level)}
                  </strong>
                </div>
                <div>
                  <span>Demande analysée</span>
                  <strong>{iamAnalysisResult.request}</strong>
                </div>
              </div>

              <div className="analysis-grid">
                <article>
                  <h3>Services détectés</h3>
                  <div className="analysis-chip-list">
                    {iamAnalysisResult.services.length > 0 ? (
                      iamAnalysisResult.services.map((service) => (
                        <span className="analysis-chip" key={service}>
                          {service}
                        </span>
                      ))
                    ) : (
                      <span className="missing-badge">Non détecté</span>
                    )}
                  </div>
                </article>
                <article>
                  <h3>Intentions détectées</h3>
                  <div className="analysis-chip-list">
                    {iamAnalysisResult.intents.length > 0 ? (
                      iamAnalysisResult.intents.map((intent) => (
                        <span className="analysis-chip" key={intent}>
                          {intent}
                        </span>
                      ))
                    ) : (
                      <span className="missing-badge">Non détecté</span>
                    )}
                  </div>
                </article>
              </div>

              {iamAnalysisResult.resource_arn ? (
                <div className="analysis-list-section generated-arn-section">
                  <div className="policy-section-header">
                    <div>
                      <h3>ARN généré automatiquement</h3>
                      {iamAnalysisResult.resource_name ? (
                        <p>Ressource détectée : {iamAnalysisResult.resource_name}</p>
                      ) : null}
                    </div>
                    <button type="button" onClick={copyGeneratedArn}>
                      Copier ARN
                    </button>
                  </div>
                  <pre className="policy-output">
                    {Array.isArray(iamAnalysisResult.resource_arn)
                      ? iamAnalysisResult.resource_arn.join("\n")
                      : iamAnalysisResult.resource_arn}
                  </pre>
                </div>
              ) : null}

              <div className="analysis-list-section">
                <h3>Actions IAM proposées</h3>
                {iamAnalysisResult.actions.length > 0 ? (
                  <div className="interactive-action-grid">
                    {iamAnalysisResult.actions.map((action) => (
                      <label
                        className={`interactive-action-card ${
                          selectedIamActions.includes(action)
                            ? "interactive-action-selected"
                            : ""
                        }`}
                        key={action}
                      >
                        <input
                          type="checkbox"
                          checked={selectedIamActions.includes(action)}
                          onChange={() => toggleIamAction(action)}
                        />
                        <span>
                          <strong>{action}</strong>
                          <small>{getActionDescription(action)}</small>
                        </span>
                        <em className={`risk-pill risk-${getActionRisk(action)}`}>
                          {getActionRiskLabel(getActionRisk(action))}
                        </em>
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="empty-state">Aucune action IAM proposée.</p>
                )}
              </div>

              {iamAnalysisResult.actions.length > 0 ? (
                <div className="analysis-list-section">
                  <div className="policy-section-header">
                    <h3>Policy JSON générée</h3>
                    <div className="policy-actions">
                      <button
                        type="button"
                        onClick={copyInteractivePolicyJson}
                        disabled={selectedIamActions.length === 0}
                      >
                        Copier JSON
                      </button>
                      <button
                        type="button"
                        onClick={exportInteractiveTerraform}
                        disabled={selectedIamActions.length === 0}
                      >
                        Exporter Terraform
                      </button>
                    </div>
                  </div>
                  {interactivePolicyMessage ? (
                    <p className="success-message">{interactivePolicyMessage}</p>
                  ) : null}
                  <pre className="policy-output">
                    {JSON.stringify(interactivePolicy, null, 2)}
                  </pre>
                </div>
              ) : null}

              <div className="analysis-list-section">
                <h3>Recommandations</h3>
                <ul className="analysis-list">
                  {iamAnalysisResult.recommendations.map((recommendation) => (
                    <li key={recommendation}>{recommendation}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}
        </section>

        <section className="card ai-assistant-card">
          <div className="card-header">
            <div>
              <h2>Explication pédagogique</h2>
            </div>
            <span className="muted">Assistant intelligent</span>
          </div>

          <p className="helper-text">
            Posez une question pour obtenir une explication claire sur une
            permission, une policy ou un concept IAM.
          </p>

          <label className="field">
            <span>Question IAM</span>
            <textarea
              value={aiPrompt}
              onChange={(event) => {
                setAiPrompt(event.target.value);
                setAiError(null);
              }}
              placeholder="Pose une question IAM..."
              rows={5}
            />
          </label>

          <button
            className="ai-button"
            type="button"
            onClick={askIamAssistant}
            disabled={isAskingAi}
          >
            {isAskingAi ? "Réponse en cours..." : "Demander à l'assistant"}
          </button>

          {aiError ? <p className="error">{aiError}</p> : null}

          {aiResponse ? (
            <div className="ai-output">
              <span>Réponse pédagogique</span>
              <p>{aiResponse}</p>
            </div>
          ) : null}
        </section>

        <section className="card parser-card">
          <div className="card-header">
            <div>
              <h2>Analyse guidée</h2>
            </div>
            <span className="muted">Workflow assisté</span>
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
                <h2>Analyse de la demande</h2>
              </div>
              <span className="muted">Avant génération</span>
            </div>

            <p>
              L'assistant analyse la phrase utilisateur avant de générer les
              permissions IAM.
              Vous pouvez vérifier l'analyse avant de générer le rôle IAM.
              Une policy IAM peut contenir plusieurs permissions.
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

            {parsedRequest.permissions && parsedRequest.permissions.length > 0 ? (
              <div className="detected-permissions">
                <h3>Permissions détectées</h3>
                <div className="permission-chip-list">
                  {parsedRequest.permissions.map((permission) => (
                    <span
                      className="permission-chip"
                      key={`${permission.service}-${permission.action}-${permission.resource_name ?? "no-resource"}`}
                    >
                      <strong>{permission.service}</strong>
                      <em>{permission.action}</em>
                      {permission.resource_name ? (
                        <span>{permission.resource_name}</span>
                      ) : null}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

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
              <h2>Mode avancé</h2>
            </div>
            <span className="muted">Configuration manuelle</span>
          </div>

          <p className="helper-text">
            Les sélecteurs permettent de construire dynamiquement un rôle IAM.
            Le mode utilisateur adapte le niveau de détail des explications.
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

            <label className="field">
              <span>Mode utilisateur</span>
              <select
                value={userMode}
                onChange={(event) => setUserMode(event.target.value)}
              >
                {userModes.map((mode) => (
                  <option key={mode.value} value={mode.value}>
                    {mode.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="active-mode">
            <span>Mode actif</span>
            <strong>{formatUserMode(userMode)}</strong>
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

        {shouldShowResourceGuidance ? (
          <section className="card resource-warning-card">
            <div className="card-header">
              <div>
                <h2>Ressource AWS manquante</h2>
              </div>
              <span className="muted">ARN recommandé</span>
            </div>

            <p className="helper-text">
              Limiter Resource permet d'appliquer le principe du moindre
              privilège.
            </p>

            <label className="field">
              <span>ARN de la ressource</span>
              <input
                type="text"
                value={resourceArn}
                onChange={(event) => {
                  setResourceArn(event.target.value);
                  setResourceArnError(null);
                  setResourceArnMessage(null);
                }}
                placeholder="arn:aws:s3:::mon-bucket/*"
              />
            </label>

            <button type="button" onClick={applyResourceArn}>
              Appliquer l'ARN
            </button>

            {resourceArnError ? <p className="error">{resourceArnError}</p> : null}
            {resourceArnMessage ? (
              <p className="success-message">{resourceArnMessage}</p>
            ) : null}
          </section>
        ) : null}

        <section className="card history-card">
          <div className="card-header">
            <div>
              <h2>Historique des générations</h2>
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
                      Mode : {formatUserMode(entry.mode)}
                    </span>
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
            <section className="card final-preview-card">
              <div className="card-header">
                <div>
                  <h2>Aperçu final</h2>
                </div>
                <div className="final-preview-badges">
                  <span className="preview-badge preview-badge-type">
                    {formatAwsServiceType(lastGeneratedPayload?.aws_service_type)}
                  </span>
                  <span className="preview-badge preview-badge-count">
                    {permissionCount} permission{permissionCount > 1 ? "s" : ""}
                  </span>
                  {securityResult ? (
                    <span className={getSecurityBadgeClass(securityResult.level)}>
                      {formatSecurityLevel(securityResult.level)}
                    </span>
                  ) : null}
                </div>
              </div>

              <p className="helper-text">
                Cet aperçu permet de vérifier rapidement la configuration IAM
                avant utilisation.
              </p>

              <div className="final-preview-grid">
                <article>
                  <span>Nom du rôle IAM</span>
                  <strong>{roleName ?? "Non disponible"}</strong>
                </article>
                <article>
                  <span>Type AWS détecté</span>
                  <strong>
                    {formatAwsServiceType(lastGeneratedPayload?.aws_service_type)}
                  </strong>
                </article>
                <article>
                  <span>Score sécurité</span>
                  <strong>
                    {securityResult ? `${securityResult.score}/100` : "Non disponible"}
                  </strong>
                </article>
                <article>
                  <span>Niveau de sécurité</span>
                  <strong>
                    {securityResult
                      ? formatSecurityLevel(securityResult.level)
                      : "Non disponible"}
                  </strong>
                </article>
                <article>
                  <span>Nombre de findings sécurité</span>
                  <strong>{securityFindings.length}</strong>
                </article>
                <article>
                  <span>Exports disponibles</span>
                  <strong>{exportNames.join(", ")}</strong>
                </article>
              </div>

              <div className="final-permissions">
                <h3>Liste des permissions détectées</h3>
                <div className="final-permission-list">
                  {policyStatements.map((statement, index) => (
                    <article
                      className="final-permission-item"
                      key={`${statement.Action.join("-")}-${index}`}
                    >
                      <strong>{statement.Action.join(", ")}</strong>
                      <small>Ressources associées</small>
                      <span>{formatResourceValue(statement.Resource)}</span>
                    </article>
                  ))}
                </div>
              </div>
            </section>

            <section className="card result-card">
              <div className="card-header">
                <div>
                  <h2>Rôle IAM généré</h2>
                </div>
                <div className="policy-actions">
                  <button type="button" onClick={copyPolicyJson}>
                    Copier la policy JSON
                  </button>
                  <button type="button" onClick={downloadPolicyJson}>
                    Télécharger la policy JSON
                  </button>
                  <button type="button" onClick={downloadPermissionPolicyJson}>
                    Télécharger Permission Policy
                  </button>
                  <button type="button" onClick={downloadTrustPolicyJson}>
                    Télécharger Trust Policy
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

              <p className="helper-text">
                Chaque export correspond à un usage différent : IAM direct,
                CloudFormation ou Terraform.
              </p>
            </section>

            {cloudFormationTemplate ? (
              <section className="card template-card">
                <div className="card-header">
                  <div>
                    <h2>Template CloudFormation</h2>
                  </div>
                  <div className="policy-actions">
                    <button type="button" onClick={copyCloudFormationTemplate}>
                      Copier CloudFormation
                    </button>
                    <button type="button" onClick={downloadCloudFormationYaml}>
                      Télécharger CloudFormation YAML
                    </button>
                  </div>
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
                    <h2>Template Terraform</h2>
                  </div>
                  <div className="policy-actions">
                    <button type="button" onClick={copyTerraformTemplate}>
                      Copier Terraform
                    </button>
                    <button type="button" onClick={downloadTerraformTf}>
                      Télécharger Terraform TF
                    </button>
                  </div>
                </div>
                <p>
                  Terraform permet de gérer l'infrastructure cloud sous forme
                  de code.
                </p>
                <pre className="policy-output">{terraformTemplate}</pre>
              </section>
            ) : null}

            <section className="card export-help-card">
              <div className="card-header">
                <div>
                  <h2>Quel fichier utiliser ?</h2>
                </div>
                <span className="muted">Exports</span>
              </div>

              <div className="export-help-grid">
                <article>
                  <strong>Permission Policy JSON</strong>
                  <p>
                    À coller dans IAM comme policy de permissions.
                  </p>
                </article>
                <article>
                  <strong>Trust Policy JSON</strong>
                  <p>
                    Définit quel service AWS peut utiliser le rôle.
                  </p>
                </article>
                <article>
                  <strong>CloudFormation YAML</strong>
                  <p>
                    Pour créer le rôle via AWS CloudFormation.
                  </p>
                </article>
                <article>
                  <strong>Terraform TF</strong>
                  <p>
                    Pour créer le rôle via Terraform.
                  </p>
                </article>
              </div>

              <p className="helper-text">
                Ces exports ne déploient rien automatiquement : ils servent de
                base à vérifier puis importer dans AWS.
              </p>
            </section>

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
          <h2>Évolutions à venir</h2>
          <p>
            Validation avancée des permissions, simulation IAM et analyse de
            policies existantes.
          </p>
        </section>
      </div>
    </main>
  );
}
