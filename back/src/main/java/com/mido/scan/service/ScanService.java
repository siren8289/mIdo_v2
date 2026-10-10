package com.mido.scan.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.mido.ai.AiClient;
import com.mido.global.exception.ApiException;
import com.mido.scan.dto.ScanRequest;
import com.mido.scan.entity.Scan;
import com.mido.scan.repository.ScanRepository;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 메인 기능 1: 의존성 위험 분석
 *   1. 프론트 입력을 AI 서버에 보낸다
 *   2. AI 결과를 DB에 저장한다
 *   3. 저장된 결과를 돌려준다
 */
@Service
public class ScanService {

    private final AiClient aiClient;
    private final ScanRepository scanRepository;

    public ScanService(AiClient aiClient, ScanRepository scanRepository) {
        this.aiClient = aiClient;
        this.scanRepository = scanRepository;
    }

    public Scan analyze(ScanRequest request) {
        JsonNode ai = aiClient.analyze(request.getManifest());
        JsonNode summary = ai.path("summary");

        Scan scan = new Scan();
        scan.setFileType(ai.path("file_type").asText());
        scan.setDependencyCount(summary.path("dependency_count").asInt());
        scan.setVulnerabilityCount(summary.path("vulnerability_count").asInt());
        scan.setKevCount(summary.path("kev_count").asInt());
        scan.setLevel(summary.path("level").asText());
        scan.setExplanation(ai.path("explanation").asText());
        scan.setExplanationSource(ai.path("explanation_source").asText());
        scan.setFindingsJson(ai.toString());
        return scanRepository.save(scan);
    }

    public Scan get(Long id) {
        Scan scan = scanRepository.findById(id).orElse(null);
        if (scan == null) {
            throw ApiException.notFound("분석 기록이 없습니다. id=" + id);
        }
        return scan;
    }

    public List<Scan> recent() {
        return scanRepository.findTop10ByOrderByIdDesc();
    }
}
