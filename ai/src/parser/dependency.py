"""사용자가 붙여 넣은 의존성 파일에서 '라이브러리 이름 + 버전'을 뽑는다.

지원하는 파일 4종:
  package.json      (npm)    "lodash": "^4.17.15"
  requirements.txt  (PyPI)   requests==2.19.0
  build.gradle      (Maven)  implementation 'org.apache.logging.log4j:log4j-core:2.14.1'
  pom.xml           (Maven)  <groupId>..</groupId><artifactId>..</artifactId><version>..</version>

버전이 정확히 정해지지 않은 줄(예: requests>=2.0)은 어떤 버전인지 알 수 없어서 건너뛴다.
"""
import json
import re

from src.core.config import MAX_DEPENDENCIES

GRADLE_PATTERN = re.compile(
    r"(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(?\s*['\"]([^:'\"]+):([^:'\"]+):([^:'\"]+)['\"]"
)
MAVEN_PATTERN = re.compile(
    r"<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?<version>([^<]+)</version>.*?</dependency>",
    re.DOTALL,
)
PYPI_PATTERN = re.compile(r"^([A-Za-z0-9_.\-\[\]]+)\s*==\s*([A-Za-z0-9_.\-]+)")


def detect_file_type(text: str) -> str:
    """글 모양을 보고 어떤 파일인지 추측한다."""
    stripped = text.strip()
    if stripped.startswith("{"):
        return "package.json"
    if "<project" in stripped or "<dependency>" in stripped:
        return "pom.xml"
    if GRADLE_PATTERN.search(stripped):
        return "build.gradle"
    return "requirements.txt"


def clean_version(version: str):
    """'^4.17.15' → '4.17.15'. 숫자로 시작하지 않으면(예: 'latest', '*') None."""
    version = version.strip().lstrip("^~=v")
    return version if re.match(r"^\d", version) else None


def parse_package_json(text: str):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    result = []
    for section in ["dependencies", "devDependencies"]:
        for name, version in (data.get(section) or {}).items():
            version = clean_version(str(version))
            if version:
                result.append({"ecosystem": "npm", "name": name, "version": version})
    return result


def parse_requirements(text: str):
    result = []
    for line in text.splitlines():
        line = line.split("#")[0].strip()  # 주석 제거
        match = PYPI_PATTERN.match(line)
        if match:
            name = re.sub(r"\[.*\]", "", match.group(1))  # requests[socks] → requests
            result.append({"ecosystem": "pypi", "name": name, "version": match.group(2)})
    return result


def parse_gradle(text: str):
    result = []
    for group, artifact, version in GRADLE_PATTERN.findall(text):
        version = clean_version(version)
        if version:
            result.append({"ecosystem": "maven", "name": f"{group}:{artifact}", "version": version})
    return result


def parse_pom(text: str):
    result = []
    for group, artifact, version in MAVEN_PATTERN.findall(text):
        version = clean_version(version)
        # ${spring.version} 같은 변수는 실제 버전을 알 수 없어서 뺀다.
        if version:
            result.append({"ecosystem": "maven", "name": f"{group.strip()}:{artifact.strip()}", "version": version})
    return result


PARSERS = {
    "package.json": parse_package_json,
    "requirements.txt": parse_requirements,
    "build.gradle": parse_gradle,
    "pom.xml": parse_pom,
}


def parse_dependencies(text: str):
    """(파일 종류, 의존성 리스트)를 돌려준다. 같은 라이브러리가 두 번 나오면 하나만 남긴다."""
    file_type = detect_file_type(text)
    unique = {}
    for dependency in PARSERS[file_type](text):
        key = (dependency["ecosystem"], dependency["name"], dependency["version"])
        unique.setdefault(key, dependency)
    return file_type, list(unique.values())[:MAX_DEPENDENCIES]
