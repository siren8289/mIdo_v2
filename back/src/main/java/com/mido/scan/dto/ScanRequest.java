package com.mido.scan.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/** 기능 1 요청: 의존성 파일 내용 */
public class ScanRequest {

    @NotBlank
    @Size(min = 3, max = 80000)
    private String manifest;

    public String getManifest() { return manifest; }
    public void setManifest(String manifest) { this.manifest = manifest; }
}
