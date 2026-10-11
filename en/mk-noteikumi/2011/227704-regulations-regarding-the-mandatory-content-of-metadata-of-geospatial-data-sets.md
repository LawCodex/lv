---
title: "Regulations Regarding the Mandatory Content of Metadata of Geospatial Data Sets"
identifier: "MK noteikumi Nr. 211"
likumi_lv_id: 227704
type: regulation
jurisdiction: lv
language: en
translation: true
translation_of: "https://likumi.lv/ta/id/227704-noteikumi-par-geotelpisko-datu-kopu-metadatu-obligato-saturu"
title_lv: "Noteikumi par ģeotelpisko datu kopu metadatu obligāto saturu"
translator: "Valsts valodas centrs (State Language Centre)"
number: "211"
issuer: "Cabinet of Ministers"
date: 2011-03-22
entry_into_force: 2011-03-26
status: in_force
source: "https://likumi.lv/ta/en/en/id/227704-regulations-regarding-the-mandatory-content-of-metadata-of-geospatial-data-sets"
retrieved: 2026-10-12
---

# Regulations Regarding the Mandatory Content of Metadata of Geospatial Data Sets

Republic of Latvia

**Cabinet
Regulation No. 211**
Adopted 22 March 2011

Issued pursuant to Section 21, Paragraph two
of the Geospatial Information Law

1. This Regulation prescribes the mandatory content of metadata of geospatial data sets (hereinafter - metadata).

2. A holder of geospatial data set shall ensure the conformity of the mandatory content of metadata with the requirements of Commission Regulation (EC) No 1205/2008 of 3 December 2008 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards metadata (hereinafter - Commission Regulation No 1205/2008).

3. A holder of geospatial data set shall supplement the mandatory content of metadata with the following metadata information (Annex) in addition to the mandatory content of metadata specified in Commission Regulation No 1205/2008:

3.1. identification information of the geospatial data set:

3.1.1. resource format, in which data format of the geospatial data set shall be indicated;

3.1.2. version of the resource format, in which version of the data format of the geospatial data set shall be indicated;

3.1.3. identifier of a coordinate system, in which the value identifying the coordinate system used in the geospatial data set shall be indicated;

3.1.4. title of the coordinate system, in which the full title of the coordinate system used in the geospatial data set shall be indicated;

3.2. quality and validity information of the geospatial data set:

3.2.1. data completeness value and data completeness unit of measurement, in which the numerical value of existence of the objects or coverage guaranteed in the geospatial data set shall be indicated in percentage;

3.2.2. accuracy of position, in which the conformity of location of geospatial data set objects with the values, which are recognised or are true, shall be indicated.

4. A holder of geospatial data set shall ensure updating of the mandatory content of metadata not later than within 10 working days after making of changes in the geospatial data set.

5. Paragraph 3 of this Regulation shall be applied:

5.1. from 1 July 2011 - to the data sets of the holder of geospatial data sets to be currently maintained;

5.2. from 1 January 2012 - to the historical geospatial data sets under the supervision of the holder of geospatial data sets.

## Informative Reference to the European Union Directive

This Regulation contains legal norms arising from Directive 2007/2/EC of the European Parliament and of the Council of 14 March 2007 establishing an Infrastructure for Spatial Information in the European Community (INSPIRE).

Prime Minister V. Dombrovskis

Deputy Prime Minister, Minister for Defence A. Pabriks

**Annex**
Cabinet Regulation No. 211
22 March 2011

## Metadata of Geospatial Data Sets and Description thereof in Addition to the Mandatory Content of Metadata Specified in Commission Regulation (EC) No 1205/2008 of 3 December 2008 implementing Directive 2007/2/EC of the European Parliament and of the Council as Regards Metadata

<table>
 <tr>
 <td>No.</td> <td>Metadata element</td> <td>Multiplicity</td> <td>Obligation</td> <td>Description</td> <td>Value</td> </tr>
 <tr>
 <td>1.</td> <td colspan="5">Identification</td> </tr>
 <tr>
 <td>1.1.</td> <td>Resource format title</td> <td>1..*</td> <td>M</td> <td>Characterises the format of the resource. Description of the structure of the computer language, which determines the depiction of data objects in the entry, file, report, memory device or transmission channel (for example, <i>ArcGIS</i> geographic database, <i>SHP, DGN, DXF, TIFF, JEPG</i>)</td> <td>Free text</td> </tr>
 <tr>
 <td>1.2.</td> <td>Version of the resource format</td> <td>0..*</td> <td>C</td> <td>Mandatory if version of the resource format may be defined. Characterised by the number of the format version, with which the resource has been prepared (for example, <i>ArcView 3.2</i> or <i>ArcGIS 9.3.1</i>)</td> <td>Free text</td> </tr>
 <tr>
 <td>1.3.</td> <td>Identifier of the coordinate system</td> <td>0..*</td> <td>C</td> <td>Mandatory if the coordinate system of geospatial data set may be defined. Identifier of the title of the coordinate system (for example, LKS92, WGS84)</td> <td>Free text</td> </tr>
 <tr>
 <td>1.4.</td> <td>Title of the coordinate system</td> <td>0..*</td> <td>C</td> <td>Mandatory if the coordinate system of data set may be defined. Full title of the coordinate system (Geodetic Co-ordinate System of Latvia (1992))</td> <td>Free text</td> </tr>
 <tr>
 <td>2.</td> <td colspan="5">Quality and Validity</td> </tr>
 <tr>
 <td>2.1.</td> <td>Data completeness value</td> <td>0..*</td> <td>C</td> <td rowspan="2">Mandatory if the value of data completeness for geospatial data set is known. The number of data completeness value indicates the percentage of existence of terrain objects or coverage guaranteed (for example, 100 %).</td> <td>Integer</td> </tr>
 <tr>
 <td>2.2.</td> <td>Data completeness unit of measurement</td> <td>0..*</td> <td>C</td> <td>%</td> </tr>
 <tr>
 <td>2.3.</td> <td>Accuracy of position</td> <td>0..*</td> <td>C</td> <td>Mandatory, if the accuracy of position is known. The conformity of the location of geospatial data set objects shall be indicated for values, which are recognised or are true (for example, standard error - 50 m).</td> <td>Free text</td> </tr>
 </table>

Notes.

1. 1..* - there shall be only one instance of this metadata element in a result set.

2. 0..* - the presence of the relevant metadata element in a result set is conditional but the metadata element may occur once or more.

3. M - to be completed mandatorily.

4. C - mandatory, if the characteristics of data set may be defined or is known.

Deputy Prime Minister, Minister for Defence A.Pabriks

Translation © 2013 Valsts valodas centrs (State Language Centre)
