# ETDMiner

ETDMiner consists of multiple AI based applications and datasets which helps to parse, extract, classify, and mine Electronic Theses and Dissertations (ETDs).

## Table of Contents

- [AutoMeta](#autometa)
- [data](#dataset)
- [etd_crf](#etd_crf)
- [etd_segmentation](#etd_segmentation)
- [metadata_correction](#metadata_correction)
- [html_parser](#html_parser)
- [samples](#samples)
- [src](#src)
- [webcrawler](#webcrawler)

### AutoMeta

This application is [version 1.1](https://github.com/lamps-lab/AutoMeta) of [etd_crf](etd_crf/) to extract metadata automatically from scanned ETDs.

### data
It contains the dataset which is used to extract metadata from scanned ETD.

### etd_crf
It is the AutoMeta tool version 1.0.

### etd_segmentation
This is ETD segmentation tool to classify ETD pages.

### metadata_correction

This is an application to fill out the missing metadata in the database (i.e., pates_etds).

[Go to the sub-folder](metadata_correction/src/)

### samples
It contains the sample dataset which has been tested out in the above process.

### src
It contains the handful of source file to pre process dataset.

### html_parser
It contains the code and instruction to get ETDs in html file.

### webcrawler
Contains the crawlers & parsers for different universities developed to collect ETDs and extract metadata from the webpages.
