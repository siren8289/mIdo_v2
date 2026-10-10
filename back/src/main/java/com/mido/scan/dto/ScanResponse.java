package com.mido.scan.dto;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mido.scan.entity.Scan;

import java.time.LocalDateTime;

/** 화면에 보내는 분석 결과. DB의 JSON 글자를 다시 객체로 풀어 준다. */
public class ScanResponse {

    private Long id;
    private String fileType;
    private int dependencyCount;
    private int vulnerabilityCount;
    private int kevCount;
    private String level;
    private String explanation;
    private String explanationSource;
    private JsonNode findingsJson;
    private LocalDateTime createdAt;

    public static ScanResponse from(Scan scan, ObjectMapper mapper) {
        ScanResponse response = new ScanResponse();
        response.id = scan.getId();
        response.fileType = scan.getFileType();
        response.dependencyCount = scan.getDependencyCount();
        response.vulnerabilityCount = scan.getVulnerabilityCount();
        response.kevCount = scan.getKevCount();
        response.level = scan.getLevel();
        response.explanation = scan.getExplanation();
        response.explanationSource = scan.getExplanationSource();
        response.createdAt = scan.getCreatedAt();
        try {
            response.findingsJson = mapper.readTree(scan.getFindingsJson() == null ? "{}" : scan.getFindingsJson());
        } catch (Exception e) {
            response.findingsJson = mapper.createObjectNode();
        }
        return response;
    }

    public Long getId() { return id; }
    public String getFileType() { return fileType; }
    public int getDependencyCount() { return dependencyCount; }
    public int getVulnerabilityCount() { return vulnerabilityCount; }
    public int getKevCount() { return kevCount; }
    public String getLevel() { return level; }
    public String getExplanation() { return explanation; }
    public String getExplanationSource() { return explanationSource; }
    public JsonNode getFindingsJson() { return findingsJson; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
