package com.mido.scan.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

import java.time.LocalDateTime;

/**
 * 분석 기록 1건 = scan 테이블의 한 줄.
 * 사용자 입력과 AI 결과를 함께 저장해서, 나중에 결과 화면을 다시 볼 수 있게 한다.
 */
@Entity
@Table(name = "scan")
public class Scan {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String fileType;
    private int dependencyCount;
    private int vulnerabilityCount;
    private int kevCount;
    private String level;

    @Column(length = 4000)
    private String explanation;
    private String explanationSource;

    @Lob
    @Column(columnDefinition = "CLOB")
    private String findingsJson;

    private LocalDateTime createdAt = LocalDateTime.now();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getFileType() { return fileType; }
    public void setFileType(String fileType) { this.fileType = fileType; }

    public int getDependencyCount() { return dependencyCount; }
    public void setDependencyCount(int dependencyCount) { this.dependencyCount = dependencyCount; }

    public int getVulnerabilityCount() { return vulnerabilityCount; }
    public void setVulnerabilityCount(int vulnerabilityCount) { this.vulnerabilityCount = vulnerabilityCount; }

    public int getKevCount() { return kevCount; }
    public void setKevCount(int kevCount) { this.kevCount = kevCount; }

    public String getLevel() { return level; }
    public void setLevel(String level) { this.level = level; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public String getExplanationSource() { return explanationSource; }
    public void setExplanationSource(String explanationSource) { this.explanationSource = explanationSource; }

    public String getFindingsJson() { return findingsJson; }
    public void setFindingsJson(String findingsJson) { this.findingsJson = findingsJson; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
