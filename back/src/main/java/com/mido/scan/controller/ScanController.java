package com.mido.scan.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mido.scan.dto.ScanRequest;
import com.mido.scan.dto.ScanResponse;
import com.mido.scan.service.ScanService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * POST /api/scans        분석 실행 + 저장
 * GET  /api/scans/{id}   분석 결과 다시 보기
 * GET  /api/scans        최근 분석 10건
 */
@RestController
@RequestMapping("/api/scans")
public class ScanController {

    private final ScanService scanService;
    private final ObjectMapper objectMapper;

    public ScanController(ScanService scanService, ObjectMapper objectMapper) {
        this.scanService = scanService;
        this.objectMapper = objectMapper;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ScanResponse create(@Valid @RequestBody ScanRequest request) {
        return ScanResponse.from(scanService.analyze(request), objectMapper);
    }

    @GetMapping("/{id}")
    public ScanResponse get(@PathVariable Long id) {
        return ScanResponse.from(scanService.get(id), objectMapper);
    }

    @GetMapping
    public List<ScanResponse> recent() {
        return scanService.recent().stream()
                .map(scan -> ScanResponse.from(scan, objectMapper))
                .toList();
    }
}
