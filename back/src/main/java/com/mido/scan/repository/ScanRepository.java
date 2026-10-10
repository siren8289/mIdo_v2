package com.mido.scan.repository;

import com.mido.scan.entity.Scan;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/** 메서드 이름만 적으면 Spring Data JPA가 SQL을 만들어 준다. */
public interface ScanRepository extends JpaRepository<Scan, Long> {

    List<Scan> findTop10ByOrderByIdDesc();
}
