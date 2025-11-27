import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import altair as alt

TICKER_DATA = [
    {"category": "Asset Management", "name": "Investor AB (publ)", "ticker": "INVE-B.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Atlas Copco AB (publ)", "ticker": "ATCO-A.ST"},
    {"category": "Farm & Heavy Construction Machinery", "name": "AB Volvo (publ)", "ticker": "VOLV-B.ST"},
    {"category": "Asset Management", "name": "EQT AB (publ)", "ticker": "EQT.ST"},
    {"category": "Security & Protection Services", "name": "ASSA ABLOY AB (publ)", "ticker": "ASSA-B.ST"},
    {"category": "Banks - Regional", "name": "Skandinaviska Enskilda Banken AB (publ)", "ticker": "SEB-A.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Sandvik AB (publ)", "ticker": "SAND.ST"},
    {"category": "Banks - Regional", "name": "Swedbank AB (publ)", "ticker": "SWED-A.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Hexagon AB (publ)", "ticker": "HEXA-B.ST"},
    {"category": "Aerospace & Defense", "name": "Saab AB (publ)", "ticker": "SAAB-B.ST"},
    {"category": "Apparel Manufacturing", "name": "H & M Hennes & Mauritz AB (publ)", "ticker": "HM-B.ST"},
    {"category": "Banks - Diversified", "name": "Svenska Handelsbanken AB (publ)", "ticker": "SHB-A.ST"},
    {"category": "Banks - Regional", "name": "Arion banki hf.", "ticker": "ARION-SDB.ST"},
    {"category": "Farm & Heavy Construction Machinery", "name": "Epiroc AB (publ)", "ticker": "EPI-A.ST"},
    {"category": "Drug Manufacturers - General", "name": "AstraZeneca PLC", "ticker": "AZN.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Alfa Laval AB (publ)", "ticker": "ALFA.ST"},
    {"category": "Household & Personal Products", "name": "Essity AB (publ)", "ticker": "ESSITY-B.ST"},
    {"category": "Asset Management", "name": "AB Industrivärden (publ)", "ticker": "INDU-C.ST"},
    {"category": "Conglomerates", "name": "Lifco AB (publ)", "ticker": "LIFCO-B.ST"},
    {"category": "Telecom Services", "name": "Telia Company AB (publ)", "ticker": "TELIA.ST"},
    {"category": "Conglomerates", "name": "Investment AB Latour (publ)", "ticker": "LATO-B.ST"},
    {"category": "Electrical Equipment & Parts", "name": "ABB Ltd", "ticker": "ABB.ST"},
    {"category": "Gambling", "name": "Evolution AB (publ)", "ticker": "EVO.ST"},
    {"category": "Other Industrial Metals & Mining", "name": "Boliden AB (publ)", "ticker": "BOL.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Swedish Orphan Biovitrum AB (publ)", "ticker": "SOBI.ST"},
    {"category": "Tools & Accessories", "name": "AB SKF (publ)", "ticker": "SKF-B.ST"},
    {"category": "Telecom Services", "name": "Tele2 AB (publ)", "ticker": "TEL2-B.ST"},
    {"category": "Engineering & Construction", "name": "Skanska AB (publ)", "ticker": "SKA-B.ST"},
    {"category": "Auto Manufacturers", "name": "Volvo Car AB (publ.)", "ticker": "VOLCAR-B.ST"},
    {"category": "Paper & Paper Products", "name": "Svenska Cellulosa Aktiebolaget SCA (publ)", "ticker": "SCA-B.ST"},
    {"category": "Industrial Distribution", "name": "Indutrade AB (publ)", "ticker": "INDT.ST"},
    {"category": "Industrial Distribution", "name": "Addtech AB (publ.)", "ticker": "ADDT-B.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Trelleborg AB (publ)", "ticker": "TREL-B.ST"},
    {"category": "Security & Protection Services", "name": "Securitas AB (publ)", "ticker": "SECU-B.ST"},
    {"category": "Conglomerates", "name": "L E Lundbergföretagen AB (publ)", "ticker": "LUND-B.ST"},
    {"category": "Real Estate - Diversified", "name": "Fastighets AB Balder (publ)", "ticker": "BALD-B.ST"},
    {"category": "Real Estate Services", "name": "AB Sagax (publ)", "ticker": "SAGA-B.ST"},
    {"category": "Industrial Distribution", "name": "Beijer Ref AB (publ)", "ticker": "BEIJ-B.ST"},
    {"category": "Packaged Foods", "name": "AAK AB (publ.)", "ticker": "AAK.ST"},
    {"category": "Capital Markets", "name": "Nordnet AB (publ)", "ticker": "SAVE.ST"},
    {"category": "Steel", "name": "SSAB AB (publ)", "ticker": "SSAB-B.ST"},
    {"category": "Engineering & Construction", "name": "Sweco AB (publ)", "ticker": "SWEC-B.ST"},
    {"category": "Building Products & Equipment", "name": "NIBE Industrier AB (publ)", "ticker": "NIBE-B.ST"},
    {"category": "Grocery Stores", "name": "Axfood AB (publ)", "ticker": "AXFO.ST"},
    {"category": "Paper & Paper Products", "name": "Holmen AB (publ)", "ticker": "HOLM-A.ST"},
    {"category": "Paper & Paper Products", "name": "Holmen AB (publ)", "ticker": "HOLM-B.ST"},
    {"category": "Banks - Regional", "name": "Avanza Bank Holding AB (publ)", "ticker": "AZA.ST"},
    {"category": "Medical Devices", "name": "Getinge AB (publ)", "ticker": "GETI-B.ST"},
    {"category": "Medical Devices", "name": "Sectra AB (publ)", "ticker": "SECT-B.ST"},
    {"category": "Real Estate - Development", "name": "Castellum AB (publ)", "ticker": "CAST.ST"},
    {"category": "Banks - Regional", "name": "Nordea Bank Abp", "ticker": "NDA-SE.ST"},
    {"category": "Conglomerates", "name": "Lagercrantz Group AB (publ)", "ticker": "LAGR-B.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Mycronic AB (publ)", "ticker": "MYCR.ST"},
    {"category": "Communication Equipment", "name": "Nokia Oyj", "ticker": "NOKIA-SEK.ST"},
    {"category": "Biotechnology", "name": "Camurus AB (publ)", "ticker": "CAMX.ST"},
    {"category": "Health Information Services", "name": "Asker Healthcare Group AB", "ticker": "ASKER.ST"},
    {"category": "Communication Equipment", "name": "Telefonaktiebolaget LM Ericsson (publ)", "ticker": "ERIC-B.ST"},
    {"category": "Communication Equipment", "name": "Telefonaktiebolaget LM Ericsson (publ)", "ticker": "ERIC-A.ST"},
    {"category": "Pollution & Treatment Controls", "name": "Munters Group AB (publ)", "ticker": "MTRS.ST"},
    {"category": "Real Estate Services", "name": "Wihlborgs Fastigheter AB (publ)", "ticker": "WIHL.ST"},
    {"category": "Gold", "name": "Lundin Gold Inc.", "ticker": "LUG.ST"},
    {"category": "Real Estate - Diversified", "name": "Catena AB (publ)", "ticker": "CATE.ST"},
    {"category": "Real Estate Services", "name": "Fabege AB (publ)", "ticker": "FABG.ST"},
    {"category": "Specialty Chemicals", "name": "HEXPOL AB (publ)", "ticker": "HPOL-B.ST"},
    {"category": "Leisure", "name": "Thule Group AB (publ)", "ticker": "THULE.ST"},
    {"category": "Insurance - Diversified", "name": "Sampo Oyj", "ticker": "SAMPO-SDB.ST"},
    {"category": "Real Estate - Diversified", "name": "Hufvudstaden AB (publ)", "ticker": "HUFV-A.ST"},
    {"category": "Leisure", "name": "Asmodee Group AB (publ)", "ticker": "ASMDEE-B.ST"},
    {"category": "Tools & Accessories", "name": "Husqvarna AB (publ)", "ticker": "HUSQ-A.ST"},
    {"category": "Tools & Accessories", "name": "Husqvarna AB (publ)", "ticker": "HUSQ-B.ST"},
    {"category": "Real Estate Services", "name": "Wallenstam AB (publ)", "ticker": "WALL-B.ST"},
    {"category": "Security & Protection Services", "name": "Loomis AB (publ)", "ticker": "LOOMIS.ST"},
    {"category": "Communication Equipment", "name": "HMS Networks AB (publ)", "ticker": "HMS.ST"},
    {"category": "Telecom Services", "name": "Sinch AB (publ)", "ticker": "SINCH.ST"},
    {"category": "Real Estate Services", "name": "Pandox AB (publ)", "ticker": "PNDX-B.ST"},
    {"category": "Paper & Paper Products", "name": "Billerud AB (publ)", "ticker": "BILL.ST"},
    {"category": "Asset Management", "name": "Kinnevik AB", "ticker": "KINV-B.ST"},
    {"category": "Asset Management", "name": "Kinnevik AB", "ticker": "KINV-A.ST"},
    {"category": "Copper", "name": "Lundin Mining Corporation", "ticker": "LUMI.ST"},
    {"category": "Medical Instruments & Supplies", "name": "AddLife AB (publ)", "ticker": "ALIF-B.ST"},
    {"category": "Specialty Retail", "name": "Clas Ohlson AB (publ)", "ticker": "CLAS-B.ST"},
    {"category": "Real Estate - Development", "name": "Atrium Ljungberg AB (publ)", "ticker": "ATRLJ-B.ST"},
    {"category": "Biotechnology", "name": "BioArctic AB (publ)", "ticker": "BIOA-B.ST"},
    {"category": "Asset Management", "name": "Röko AB (publ)", "ticker": "ROKO-B.ST"},
    {"category": "Engineering & Construction", "name": "NCC AB (publ)", "ticker": "NCC-B.ST"},
    {"category": "Engineering & Construction", "name": "NCC AB (publ)", "ticker": "NCC-A.ST"},
    {"category": "Lodging", "name": "Scandic Hotels Group AB (publ)", "ticker": "SHOT.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Hacksaw AB (publ)", "ticker": "HACK.ST"},
    {"category": "Steel", "name": "Alleima AB (publ)", "ticker": "ALLEI.ST"},
    {"category": "Oil & Gas E&P", "name": "International Petroleum Corporation", "ticker": "IPCO.ST"},
    {"category": "Engineering & Construction", "name": "Peab AB (publ)", "ticker": "PEAB-B.ST"},
    {"category": "Medical Devices", "name": "Vitrolife AB (publ)", "ticker": "VITR.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Embracer Group AB (publ)", "ticker": "EMBRAC-B.ST"},
    {"category": "Asset Management", "name": "Bure Equity AB (publ)", "ticker": "BURE.ST"},
    {"category": "Industrial Distribution", "name": "Bufab AB (publ)", "ticker": "BUFAB.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Electrolux Professional AB (publ)", "ticker": "EPRO-B.ST"},
    {"category": "Medical Care Facilities", "name": "Medicover AB (publ)", "ticker": "MCOV-B.ST"},
    {"category": "Gambling", "name": "Betsson AB (publ)", "ticker": "BETS-B.ST"},
    {"category": "Conglomerates", "name": "Storskogen Group AB (publ)", "ticker": "STOR-B.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Paradox Interactive AB (publ)", "ticker": "PDX.ST"},
    {"category": "Engineering & Construction", "name": "Afry AB", "ticker": "AFRY.ST"},
    {"category": "Real Estate Services", "name": "NP3 Fastigheter AB (publ)", "ticker": "NP3.ST"},
    {"category": "Industrial Distribution", "name": "OEM International AB (publ)", "ticker": "OEM-B.ST"},
    {"category": "Electrical Equipment & Parts", "name": "AQ Group AB (publ)", "ticker": "AQ.ST"},
    {"category": "Building Products & Equipment", "name": "Lindab International AB (publ)", "ticker": "LIAB.ST"},
    {"category": "Medical Devices", "name": "Elekta AB (publ)", "ticker": "EKTA-B.ST"},
    {"category": "Internet Content & Information", "name": "Hemnet Group AB (publ)", "ticker": "HEM.ST"},
    {"category": "Engineering & Construction", "name": "Bravida Holding AB (publ)", "ticker": "BRAV.ST"},
    {"category": "Furnishings, Fixtures & Appliances", "name": "AB Electrolux (publ)", "ticker": "ELUX-B.ST"},
    {"category": "Furnishings, Fixtures & Appliances", "name": "AB Electrolux (publ)", "ticker": "ELUX-A.ST"},
    {"category": "Real Estate Services", "name": "Intea Fastigheter AB (publ)", "ticker": "INTEA-B.ST"},
    {"category": "Building Products & Equipment", "name": "Systemair AB (publ)", "ticker": "SYSR.ST"},
    {"category": "Diagnostics & Research", "name": "Vimian Group AB (publ)", "ticker": "VIMIAN.ST"},
    {"category": "Real Estate Services", "name": "Nyfosa AB (publ)", "ticker": "NYF.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Beijer Alma AB (publ)", "ticker": "BEIA-B.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Alimak Group AB (publ)", "ticker": "ALIG.ST"},
    {"category": "Aluminum", "name": "Gränges AB (publ)", "ticker": "GRNG.ST"},
    {"category": "Medical Devices", "name": "Nolato AB (publ)", "ticker": "NOLA-B.ST"},
    {"category": "Farm & Heavy Construction Machinery", "name": "Traton SE", "ticker": "8TRA.ST"},
    {"category": "Banks - Regional", "name": "Norion Bank AB (publ)", "ticker": "NORION.ST"},
    {"category": "Information Technology Services", "name": "Addnode Group AB (publ)", "ticker": "ANOD-B.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Modern Times Group MTG AB", "ticker": "MTG-A.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Modern Times Group MTG AB", "ticker": "MTG-B.ST"},
    {"category": "Leisure", "name": "Dometic Group AB (publ)", "ticker": "DOM.ST"},
    {"category": "Medical Instruments & Supplies", "name": "Bonesupport Holding AB (publ)", "ticker": "BONEX.ST"},
    {"category": "Real Estate Services", "name": "Cibus Nordic Real Estate AB (publ)", "ticker": "CIBUS.ST"},
    {"category": "Communication Equipment", "name": "Invisio AB (publ)", "ticker": "IVSO.ST"},
    {"category": "Medical Care Facilities", "name": "Attendo AB (publ)", "ticker": "ATT.ST"},
    {"category": "Resorts & Casinos", "name": "SkiStar AB (publ)", "ticker": "SKIS-B.ST"},
    {"category": "Auto & Truck Dealerships", "name": "Bilia AB (publ)", "ticker": "BILI-A.ST"},
    {"category": "Engineering & Construction", "name": "Ratos AB (publ)", "ticker": "RATO-B.ST"},
    {"category": "Engineering & Construction", "name": "Ratos AB (publ)", "ticker": "RATO-A.ST"},
    {"category": "Software - Application", "name": "Vitec Software Group AB (publ)", "ticker": "VIT-B.ST"},
    {"category": "Banks - Regional", "name": "TF Bank AB (publ)", "ticker": "TFBANK.ST"},
    {"category": "Specialty Business Services", "name": "Karnov Group AB (publ)", "ticker": "KAR.ST"},
    {"category": "Medical Care Facilities", "name": "Ambea AB (publ)", "ticker": "AMBEA.ST"},
    {"category": "Specialty Retail", "name": "New Wave Group AB (publ)", "ticker": "NEWA-B.ST"},
    {"category": "Department Stores", "name": "Rusta AB (publ)", "ticker": "RUSTA.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "BioGaia AB (publ)", "ticker": "BIOG-B.ST"},
    {"category": "Real Estate - Diversified", "name": "Corem Property Group AB (publ)", "ticker": "CORE-B.ST"},
    {"category": "Real Estate - Diversified", "name": "Corem Property Group AB (publ)", "ticker": "CORE-A.ST"},
    {"category": "Real Estate - Diversified", "name": "Corem Property Group AB (publ)", "ticker": "CORE-D.ST"},
    {"category": "Electronic Components", "name": "NCAB Group AB (publ)", "ticker": "NCAB.ST"},
    {"category": "Education & Training Services", "name": "AcadeMedia AB (publ)", "ticker": "ACAD.ST"},
    {"category": "Capital Markets", "name": "CoinShares International Limited", "ticker": "CS.ST"},
    {"category": "Real Estate - Diversified", "name": "FastPartner AB (publ)", "ticker": "FPAR-A.ST"},
    {"category": "Real Estate - Diversified", "name": "FastPartner AB (publ)", "ticker": "FPAR-D.ST"},
    {"category": "Confectioners", "name": "Cloetta AB (publ)", "ticker": "CLA-B.ST"},
    {"category": "Medical Instruments & Supplies", "name": "Dynavox Group AB (publ)", "ticker": "DYVOX.ST"},
    {"category": "Conglomerates", "name": "Volati AB (publ)", "ticker": "VOLO.ST"},
    {"category": "Pharmaceutical Retailers", "name": "Apotea AB (publ)", "ticker": "APOTEA.ST"},
    {"category": "Auto Parts", "name": "Autoliv, Inc.", "ticker": "ALIV-SDB.ST"},
    {"category": "Real Estate - Diversified", "name": "Diös Fastigheter AB (publ)", "ticker": "DIOS.ST"},
    {"category": "Medical Instruments & Supplies", "name": "Synsam AB (publ)", "ticker": "SYNSAM.ST"},
    {"category": "Real Estate Services", "name": "Swedish Logistic Property AB", "ticker": "SLP-B.ST"},
    {"category": "Auto Parts", "name": "VBG Group AB (publ)", "ticker": "VBG-B.ST"},
    {"category": "Residential Construction", "name": "JM AB (publ)", "ticker": "JM.ST"},
    {"category": "Farm & Heavy Construction Machinery", "name": "engcon AB (publ)", "ticker": "ENGCON-B.ST"},
    {"category": "Credit Services", "name": "Hoist Finance AB (publ)", "ticker": "HOFI.ST"},
    {"category": "Conglomerates", "name": "Bergman & Beving AB (publ)", "ticker": "BERG-B.ST"},
    {"category": "Metal Fabrication", "name": "Troax Group AB (publ)", "ticker": "TROAX.ST"},
    {"category": "Leisure", "name": "Mips AB (publ)", "ticker": "MIPS.ST"},
    {"category": "Building Products & Equipment", "name": "Inwido AB (publ)", "ticker": "INWI.ST"},
    {"category": "Medical Devices", "name": "MedCap AB (publ)", "ticker": "MCAP.ST"},
    {"category": "Paper & Paper Products", "name": "Stora Enso Oyj", "ticker": "STE-R.ST"},
    {"category": "Paper & Paper Products", "name": "Stora Enso Oyj", "ticker": "STE-A.ST"},
    {"category": "Real Estate Services", "name": "Samhällsbyggnadsbolaget i Norden AB (publ)", "ticker": "SBB-B.ST"},
    {"category": "Real Estate Services", "name": "Samhällsbyggnadsbolaget i Norden AB (publ)", "ticker": "SBB-D.ST"},
    {"category": "Medical Distribution", "name": "Arjo AB (publ)", "ticker": "ARJO-B.ST"},
    {"category": "Real Estate Services", "name": "Sveafastigheter AB (publ)", "ticker": "SVEAF.ST"},
    {"category": "Industrial Distribution", "name": "Momentum Group AB (publ)", "ticker": "MMGR-B.ST"},
    {"category": "Software - Infrastructure", "name": "Yubico AB", "ticker": "YUBICO.ST"},
    {"category": "Real Estate Services", "name": "Logistea AB (publ)", "ticker": "LOGI-A.ST"},
    {"category": "Real Estate Services", "name": "Logistea AB (publ)", "ticker": "LOGI-B.ST"},
    {"category": "Software - Application", "name": "Truecaller AB (publ)", "ticker": "TRUE-B.ST"},
    {"category": "Electrical Equipment & Parts", "name": "Fagerhult Group AB", "ticker": "FAG.ST"},
    {"category": "Real Estate Services", "name": "Platzer Fastigheter Holding AB (publ)", "ticker": "PLAZ-B.ST"},
    {"category": "Credit Services", "name": "Resurs Bank AB (publ)", "ticker": "RESURS.ST"},
    {"category": "Apparel Retail", "name": "RVRC Holding AB (publ)", "ticker": "RVRC.ST"},
    {"category": "Apparel Retail", "name": "Boozt AB (publ)", "ticker": "BOOZT.ST"},
    {"category": "Infrastructure Operations", "name": "Sdiptech AB (publ)", "ticker": "SDIP-B.ST"},
    {"category": "Asset Management", "name": "Creades AB", "ticker": "CRED-A.ST"},
    {"category": "Marine Shipping", "name": "Rederiaktiebolaget Gotland (publ)", "ticker": "GOTL-B.ST"},
    {"category": "Marine Shipping", "name": "Rederiaktiebolaget Gotland (publ)", "ticker": "GOTL-A.ST"},
    {"category": "Real Estate Services", "name": "Fastighetsbolaget Emilshus AB (publ)", "ticker": "EMIL-B.ST"},
    {"category": "Health Information Services", "name": "RaySearch Laboratories AB (publ)", "ticker": "RAY-B.ST"},
    {"category": "Packaged Foods", "name": "Scandi Standard AB (publ)", "ticker": "SCST.ST"},
    {"category": "Aerospace & Defense", "name": "MilDef Group AB (publ)", "ticker": "MILDEF.ST"},
    {"category": "Publishing", "name": "Storytel AB (publ)", "ticker": "STORY-B.ST"},
    {"category": "Engineering & Construction", "name": "Instalco AB (publ)", "ticker": "INSTAL.ST"},
    {"category": "Industrial Distribution", "name": "Alligo AB (publ)", "ticker": "ALLIGO-B.ST"},
    {"category": "Asset Management", "name": "Svolder AB (publ)", "ticker": "SVOL-B.ST"},
    {"category": "Electronic Components", "name": "Hanza AB (publ)", "ticker": "HANZA.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Nederman Holding AB (publ)", "ticker": "NMAN.ST"},
    {"category": "Real Estate - Diversified", "name": "Stendörren Fastigheter AB (publ)", "ticker": "STEF-B.ST"},
    {"category": "Entertainment", "name": "Acast AB (publ)", "ticker": "ACAST.ST"},
    {"category": "Packaged Foods", "name": "Swedencare AB (publ)", "ticker": "SECARE.ST"},
    {"category": "Specialty Retail", "name": "Fenix Outdoor International AG", "ticker": "FOI-B.ST"},
    {"category": "Credit Services", "name": "Intrum AB (publ)", "ticker": "INTRUM.ST"},
    {"category": "Asset Management", "name": "Investment AB Öresund (publ)", "ticker": "ORES.ST"},
    {"category": "Medical Devices", "name": "Xvivo Perfusion AB (publ)", "ticker": "XVIVO.ST"},
    {"category": "Electronic Components", "name": "NOTE AB (publ)", "ticker": "NOTE.ST"},
    {"category": "Internet Retail", "name": "BHG Group AB (publ)", "ticker": "BHG.ST"},
    {"category": "Real Estate - Diversified", "name": "John Mattson Fastighetsföretagen AB (publ)", "ticker": "JOMA.ST"},
    {"category": "Real Estate Services", "name": "Eastnine AB (publ)", "ticker": "EAST.ST"},
    {"category": "Tobacco", "name": "Haypp Group AB (publ)", "ticker": "HAYPP.ST"},
    {"category": "Software - Application", "name": "Better Collective A/S", "ticker": "BETCO.ST"},
    {"category": "Household & Personal Products", "name": "Duni AB (publ)", "ticker": "DUNI.ST"},
    {"category": "Real Estate Services", "name": "Heba Fastighets AB (publ)", "ticker": "HEBA-B.ST"},
    {"category": "Business Equipment & Supplies", "name": "ITAB Shop Concept AB (publ)", "ticker": "ITAB.ST"},
    {"category": "Software - Application", "name": "Verve Group SE", "ticker": "VER.ST"},
    {"category": "Specialty Business Services", "name": "Coor Service Management Holding AB", "ticker": "COOR.ST"},
    {"category": "Software - Application", "name": "Lime Technologies AB (publ)", "ticker": "LIME.ST"},
    {"category": "Auto Parts", "name": "Meko AB (publ)", "ticker": "MEKO.ST"},
    {"category": "Engineering & Construction", "name": "Nyab AB (publ)", "ticker": "NYAB.ST"},
    {"category": "Telecom Services", "name": "Bahnhof AB (publ)", "ticker": "BAHN-B.ST"},
    {"category": "Entertainment", "name": "Viaplay Group AB (publ)", "ticker": "VPLAY-B.ST"},
    {"category": "Entertainment", "name": "Viaplay Group AB (publ)", "ticker": "VPLAY-A.ST"},
    {"category": "Asset Management", "name": "Linc AB", "ticker": "LINC.ST"},
    {"category": "Consulting Services", "name": "Rejlers AB (publ)", "ticker": "REJL-B.ST"},
    {"category": "Real Estate - Development", "name": "Prisma Properties AB (publ)", "ticker": "PRISMA.ST"},
    {"category": "Real Estate Services", "name": "Stenhus Fastigheter i Norden AB (publ)", "ticker": "SFAST.ST"},
    {"category": "Medical Devices", "name": "CellaVision AB (publ)", "ticker": "CEVI.ST"},
    {"category": "Packaged Foods", "name": "Zinzino AB (publ)", "ticker": "ZZ-B.ST"},
    {"category": "Health Information Services", "name": "Surgical Science Sweden AB (publ)", "ticker": "SUS.ST"},
    {"category": "Communication Equipment", "name": "Ependion AB", "ticker": "EPEN.ST"},
    {"category": "Telecom Services", "name": "Ovzon AB (publ)", "ticker": "OVZON.ST"},
    {"category": "Real Estate - Development", "name": "Besqab AB (publ)", "ticker": "BESQAB.ST"},
    {"category": "Real Estate - Diversified", "name": "Fastighets AB Trianon (publ)", "ticker": "TRIAN-B.ST"},
    {"category": "Gambling", "name": "Kambi Group plc", "ticker": "KAMBI.ST"},
    {"category": "Communication Equipment", "name": "Hexatronic Group AB (publ)", "ticker": "HTRO.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Stillfront Group AB (publ)", "ticker": "SF.ST"},
    {"category": "Asset Management", "name": "AB Traction", "ticker": "TRAC-B.ST"},
    {"category": "Packaged Foods", "name": "Humble Group AB (publ)", "ticker": "HUMBLE.ST"},
    {"category": "Residential Construction", "name": "Bonava AB (publ)", "ticker": "BONAV-A.ST"},
    {"category": "Residential Construction", "name": "Bonava AB (publ)", "ticker": "BONAV-B.ST"},
    {"category": "Software - Application", "name": "Smart Eye AB (publ)", "ticker": "SEYE.ST"},
    {"category": "Conglomerates", "name": "Karnell Group AB (publ)", "ticker": "KARNEL-B.ST"},
    {"category": "Beverages - Wineries & Distilleries", "name": "Viva Wine Group AB", "ticker": "VIVA.ST"},
    {"category": "Building Products & Equipment", "name": "Svedbergs Group AB (publ)", "ticker": "SVED-B.ST"},
    {"category": "Restaurants", "name": "Nordrest Holding AB (publ)", "ticker": "NREST.ST"},
    {"category": "Engineering & Construction", "name": "Vestum AB (publ)", "ticker": "VESTUM.ST"},
    {"category": "Information Technology Services", "name": "Knowit AB (publ)", "ticker": "KNOW.ST"},
    {"category": "Biotechnology", "name": "Flerie AB (publ)", "ticker": "FLERIE.ST"},
    {"category": "Real Estate Services", "name": "Brinova Fastigheter AB (publ)", "ticker": "BRIN-B.ST"},
    {"category": "Home Improvement Retail", "name": "Byggmax Group AB (publ)", "ticker": "BMAX.ST"},
    {"category": "Asset Management", "name": "VNV Global AB (publ)", "ticker": "VNV.ST"},
    {"category": "Residential Construction", "name": "K-Fast Holding AB (publ)", "ticker": "KFAST-B.ST"},
    {"category": "Real Estate Services", "name": "Nivika Fastigheter AB (publ)", "ticker": "NIVI-B.ST"},
    {"category": "Specialty Industrial Machinery", "name": "XANO Industri AB (publ)", "ticker": "XANO-B.ST"},
    {"category": "Industrial Distribution", "name": "Teqnion AB (publ)", "ticker": "TEQ.ST"},
    {"category": "Information Technology Services", "name": "Proact IT Group AB (publ)", "ticker": "PACT.ST"},
    {"category": "Telecom Services", "name": "Bredband2 i Skandinavien AB (publ)", "ticker": "BRE2.ST"},
    {"category": "Apparel Retail", "name": "Nelly Group AB (publ)", "ticker": "NELLY.ST"},
    {"category": "Other Industrial Metals & Mining", "name": "Gruvaktiebolaget Viscaria", "ticker": "VISC.ST"},
    {"category": "Consulting Services", "name": "BTS Group AB (publ)", "ticker": "BTS-B.ST"},
    {"category": "Biotechnology", "name": "Hansa Biopharma AB (publ)", "ticker": "HNSA.ST"},
    {"category": "Asset Management", "name": "Idun Industrier AB (publ)", "ticker": "IDUN-B.ST"},
    {"category": "Aerospace & Defense", "name": "GomSpace Group AB (publ)", "ticker": "GOMX.ST"},
    {"category": "Specialty Chemicals", "name": "KB Components AB (publ)", "ticker": "KBC.ST"},
    {"category": "Information Technology Services", "name": "Dustin Group AB (publ)", "ticker": "DUST.ST"},
    {"category": "Furnishings, Fixtures & Appliances", "name": "Nobia AB (publ)", "ticker": "NOBI.ST"},
    {"category": "Electrical Equipment & Parts", "name": "PowerCell Sweden AB (publ)", "ticker": "PCELL.ST"},
    {"category": "Biotechnology", "name": "Egetis Therapeutics AB (publ)", "ticker": "EGTX.ST"},
    {"category": "Real Estate Services", "name": "Neobo Fastigheter AB (publ)", "ticker": "NEOBO.ST"},
    {"category": "Medical Care Facilities", "name": "Humana AB (publ)", "ticker": "HUM.ST"},
    {"category": "Specialty Business Services", "name": "Green Landscaping Group AB (publ)", "ticker": "GREEN.ST"},
    {"category": "Aerospace & Defense", "name": "CTT Systems AB (publ)", "ticker": "CTT.ST"},
    {"category": "Biotechnology", "name": "Vicore Pharma Holding AB (publ)", "ticker": "VICO.ST"},
    {"category": "Asset Management", "name": "Catella AB (publ)", "ticker": "CAT-B.ST"},
    {"category": "Asset Management", "name": "Catella AB (publ)", "ticker": "CAT-A.ST"},
    {"category": "Pollution & Treatment Controls", "name": "Absolent Air Care Group AB (publ)", "ticker": "ABSO.ST"},
    {"category": "Asset Management", "name": "VEF AB (publ)", "ticker": "VEFAB.ST"},
    {"category": "Information Technology Services", "name": "TietoEVRY Oyj", "ticker": "TIETOS.ST"},
    {"category": "Real Estate Services", "name": "KlaraBo Sverige AB (publ)", "ticker": "KLARA-B.ST"},
    {"category": "Real Estate - Diversified", "name": "ALM Equity AB (publ)", "ticker": "ALM.ST"},
    {"category": "Biotechnology", "name": "Saniona AB (publ)", "ticker": "SANION.ST"},
    {"category": "Waste Management", "name": "Studsvik AB (publ)", "ticker": "SVIK.ST"},
    {"category": "Building Products & Equipment", "name": "FM Mattsson AB (publ)", "ticker": "FMM-B.ST"},
    {"category": "Specialty Business Services", "name": "Elanders AB (publ)", "ticker": "ELAN-B.ST"},
    {"category": "Biotechnology", "name": "BioInvent International AB (publ)", "ticker": "BINV.ST"},
    {"category": "Household & Personal Products", "name": "Lyko Group AB (publ)", "ticker": "LYKO-A.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Cereno Scientific AB (publ)", "ticker": "CRNO-B.ST"},
    {"category": "Health Information Services", "name": "Carasent AB (publ)", "ticker": "CARA.ST"},
    {"category": "Information Technology Services", "name": "Exsitec Holding AB (publ)", "ticker": "EXS.ST"},
    {"category": "Real Estate - Development", "name": "Arlandastad Group AB (publ)", "ticker": "AGROUP.ST"},
    {"category": "Real Estate Services", "name": "Genova Property Group AB (publ)", "ticker": "GPG.ST"},
    {"category": "Diagnostics & Research", "name": "Devyser Diagnostics AB (publ)", "ticker": "DVYSR.ST"},
    {"category": "Recreational Vehicles", "name": "KABE Group AB (publ.)", "ticker": "KABE-B.ST"},
    {"category": "Information Technology Services", "name": "Vertiseit AB (publ)", "ticker": "VERT-B.ST"},
    {"category": "Engineering & Construction", "name": "ByggPartner Gruppen AB (publ)", "ticker": "BYGGP.ST"},
    {"category": "Publishing", "name": "Byggmästare Anders J Ahlström Holding AB (publ)", "ticker": "AJA-B.ST"},
    {"category": "Asset Management", "name": "Flat Capital AB (publ)", "ticker": "FLAT-B.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "EQL Pharma AB (publ)", "ticker": "EQL.ST"},
    {"category": "Medical Instruments & Supplies", "name": "Stille AB", "ticker": "STIL.ST"},
    {"category": "Staffing & Employment Services", "name": "Ework Group AB (publ)", "ticker": "EWRK.ST"},
    {"category": "Oil & Gas E&P", "name": "Maha Capital AB (publ)", "ticker": "MAHA-A.ST"},
    {"category": "Software - Infrastructure", "name": "Enea AB (publ)", "ticker": "ENEA.ST"},
    {"category": "Electrical Equipment & Parts", "name": "Intellego Technologies AB", "ticker": "INT.ST"},
    {"category": "Utilities - Renewable", "name": "Arise AB (publ)", "ticker": "ARISE.ST"},
    {"category": "Marine Shipping", "name": "Viking Supply Ships AB (publ)", "ticker": "VSSAB-B.ST"},
    {"category": "Engineering & Construction", "name": "Fasadgruppen Group AB (publ)", "ticker": "FG.ST"},
    {"category": "Medical Devices", "name": "Paxman AB (publ)", "ticker": "PAX.ST"},
    {"category": "Communication Equipment", "name": "Net Insight AB (publ)", "ticker": "NETI-B.ST"},
    {"category": "Insurance - Specialty", "name": "Solid Försäkringsaktiebolag (publ)", "ticker": "SFAB.ST"},
    {"category": "Banks - Regional", "name": "Lea Bank AB", "ticker": "LEA.ST"},
    {"category": "Biotechnology", "name": "Oncopeptides AB (publ)", "ticker": "ONCO.ST"},
    {"category": "Biotechnology", "name": "Genovis AB (publ.)", "ticker": "GENO.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Berner Industrier AB", "ticker": "BERNER-B.ST"},
    {"category": "Telecom Services", "name": "Eltel AB (publ)", "ticker": "ELTEL.ST"},
    {"category": "Engineering & Construction", "name": "Train Alliance AB (publ)", "ticker": "TRAIN-B.ST"},
    {"category": "Medical Devices", "name": "BICO Group AB (publ)", "ticker": "BICO.ST"},
    {"category": "Biotechnology", "name": "Diamyd Medical AB (publ)", "ticker": "DMYD-B.ST"},
    {"category": "Real Estate Services", "name": "Annehem Fastigheter AB", "ticker": "ANNE-B.ST"},
    {"category": "Home Improvement Retail", "name": "RugVista Group AB (publ)", "ticker": "RUG.ST"},
    {"category": "Real Estate Services", "name": "Fortinova Fastigheter AB (Publ)", "ticker": "FNOVA-B.ST"},
    {"category": "Software - Application", "name": "Formpipe Software AB (publ)", "ticker": "FPIP.ST"},
    {"category": "Residential Construction", "name": "Studentbostäder i Norden AB (publ)", "ticker": "STUDBO.ST"},
    {"category": "Packaged Foods", "name": "Midsona AB (publ)", "ticker": "MSON-B.ST"},
    {"category": "Building Products & Equipment", "name": "Firefly AB (publ)", "ticker": "FIRE.ST"},
    {"category": "Utilities - Renewable", "name": "Orrön Energy AB (publ)", "ticker": "ORRON.ST"},
    {"category": "Utilities - Regulated Electric", "name": "Dala Energi AB (publ)", "ticker": "DE.ST"},
    {"category": "Oil & Gas E&P", "name": "Meren Energy Inc.", "ticker": "MER.ST"},
    {"category": "Medical Devices", "name": "OssDsign AB (publ)", "ticker": "OSSD.ST"},
    {"category": "Software - Application", "name": "Cint Group AB (publ)", "ticker": "CINT.ST"},
    {"category": "Biotechnology", "name": "SynAct Pharma AB", "ticker": "SYNACT.ST"},
    {"category": "Specialty Retail", "name": "Bokusgruppen AB (publ)", "ticker": "BOKUS.ST"},
    {"category": "Software - Application", "name": "Micro Systemation AB (publ)", "ticker": "MSAB-B.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Enad Global 7 AB (publ)", "ticker": "EG7.ST"},
    {"category": "Medical Devices", "name": "C-Rad AB (publ)", "ticker": "CRAD-B.ST"},
    {"category": "Food Distribution", "name": "Cheffelo AB (publ)", "ticker": "CHEF.ST"},
    {"category": "Communication Equipment", "name": "Doro AB (publ)", "ticker": "DORO.ST"},
    {"category": "Biotechnology", "name": "Xspray Pharma AB (publ)", "ticker": "XSPRAY.ST"},
    {"category": "Information Technology Services", "name": "Softronic AB (publ)", "ticker": "SOF-B.ST"},
    {"category": "Gambling", "name": "Gentoo Media Inc.", "ticker": "G2M.ST"},
    {"category": "Specialty Industrial Machinery", "name": "SaltX Technology Holding AB (publ)", "ticker": "SALT-B.ST"},
    {"category": "Specialty Chemicals", "name": "Arla Plast AB", "ticker": "ARPL.ST"},
    {"category": "Auto Parts", "name": "Bulten AB (publ)", "ticker": "BULTEN.ST"},
    {"category": "Software - Infrastructure", "name": "Clavister Holding AB (publ.)", "ticker": "CLAV.ST"},
    {"category": "Information Technology Services", "name": "Prevas AB", "ticker": "PREV-B.ST"},
    {"category": "Semiconductors", "name": "Sivers Semiconductors AB (publ)", "ticker": "SIVE.ST"},
    {"category": "Waste Management", "name": "Scandinavian Enviro Systems AB (publ)", "ticker": "SES.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Orexo AB (publ)", "ticker": "ORX.ST"},
    {"category": "Utilities - Renewable", "name": "Eolus Aktiebolag (publ)", "ticker": "EOLU-B.ST"},
    {"category": "Medical Devices", "name": "Sedana Medical AB (publ)", "ticker": "SEDANA.ST"},
    {"category": "Auto Parts", "name": "Pierce Group AB (publ)", "ticker": "PIERCE.ST"},
    {"category": "Metal Fabrication", "name": "ProfilGruppen AB (publ)", "ticker": "PROF-B.ST"},
    {"category": "Capital Markets", "name": "Mangold Fondkommission AB", "ticker": "MANG.ST"},
    {"category": "Furnishings, Fixtures & Appliances", "name": "Embellence Group AB (publ)", "ticker": "EMBELL.ST"},
    {"category": "Real Estate - Development", "name": "Tingsvalvet Fastighets AB (publ)", "ticker": "TINGS-B.ST"},
    {"category": "Real Estate - Development", "name": "Tingsvalvet Fastighets AB (publ)", "ticker": "TINGS-A.ST"},
    {"category": "Electrical Equipment & Parts", "name": "CTEK AB (publ)", "ticker": "CTEK.ST"},
    {"category": "Engineering & Construction", "name": "Nordisk Bergteknik AB (publ)", "ticker": "NORB-B.ST"},
    {"category": "Aerospace & Defense", "name": "W5 Solutions AB (publ)", "ticker": "W5.ST"},
    {"category": "Computer Hardware", "name": "Fractal Gaming Group AB (publ)", "ticker": "FRACTL.ST"},
    {"category": "Asset Management", "name": "Case Group AB (publ)", "ticker": "CASE.ST"},
    {"category": "Industrial Distribution", "name": "Inission AB (publ)", "ticker": "INISS-B.ST"},
    {"category": "Electrical Equipment & Parts", "name": "Garo Aktiebolag (publ)", "ticker": "GARO.ST"},
    {"category": "Biotechnology", "name": "Cantargia AB (publ)", "ticker": "CANTA.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Dicot Pharma AB", "ticker": "DICOT.ST"},
    {"category": "Specialty Chemicals", "name": "I-Tech AB", "ticker": "ITECH.ST"},
    {"category": "Medical Devices", "name": "Senzime AB (publ)", "ticker": "SEZI.ST"},
    {"category": "Software - Application", "name": "BIMobject AB", "ticker": "BIM.ST"},
    {"category": "Software - Application", "name": "Oneflow AB (publ)", "ticker": "ONEF.ST"},
    {"category": "Electronic Components", "name": "Acconeer AB (publ)", "ticker": "ACCON.ST"},
    {"category": "Solar", "name": "Midsummer AB (publ)", "ticker": "MIDS.ST"},
    {"category": "Information Technology Services", "name": "CAG Group AB (publ)", "ticker": "CAG.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Metacon AB (publ)", "ticker": "META.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "G5 Entertainment AB (publ)", "ticker": "G5EN.ST"},
    {"category": "Real Estate Services", "name": "Kallebäck Property Invest AB (publ)", "ticker": "KAPIAB.ST"},
    {"category": "Oil & Gas E&P", "name": "ShaMaran Petroleum Corp.", "ticker": "SNM.ST"},
    {"category": "Specialty Industrial Machinery", "name": "SinterCast AB (publ)", "ticker": "SINT.ST"},
    {"category": "Software - Application", "name": "Skolon AB (publ)", "ticker": "SKOLON.ST"},
    {"category": "Medical Instruments & Supplies", "name": "ADDvise Group AB (publ)", "ticker": "ADDV-B.ST"},
    {"category": "Medical Instruments & Supplies", "name": "ADDvise Group AB (publ)", "ticker": "ADDV-A.ST"},
    {"category": "Electronic Components", "name": "Acuvi AB", "ticker": "ACUVI.ST"},
    {"category": "Paper & Paper Products", "name": "Rottneros AB (publ)", "ticker": "RROS.ST"},
    {"category": "Information Technology Services", "name": "Novotek AB", "ticker": "NTEK-B.ST"},
    {"category": "Railroads", "name": "Railcare Group AB (publ)", "ticker": "RAIL.ST"},
    {"category": "Communication Equipment", "name": "LumenRadio AB (publ)", "ticker": "LUMEN.ST"},
    {"category": "Real Estate - Development", "name": "Doxa AB (publ)", "ticker": "DOXA.ST"},
    {"category": "Information Technology Services", "name": "CombinedX AB (publ)", "ticker": "CX.ST"},
    {"category": "Industrial Distribution", "name": "Ferronordic AB (publ)", "ticker": "FNM.ST"},
    {"category": "Software - Infrastructure", "name": "Advenica AB (publ)", "ticker": "ADVE.ST"},
    {"category": "Packaged Foods", "name": "Skåne-möllan AB (publ)", "ticker": "SKMO.ST"},
    {"category": "Biotechnology", "name": "Infant Bacterial Therapeutics AB (publ)", "ticker": "IBT-B.ST"},
    {"category": "Metal Fabrication", "name": "HAKI Safety AB (publ)", "ticker": "HAKI-B.ST"},
    {"category": "Metal Fabrication", "name": "HAKI Safety AB (publ)", "ticker": "HAKI-A.ST"},
    {"category": "Business Equipment & Supplies", "name": "Pricer AB (publ)", "ticker": "PRIC-B.ST"},
    {"category": "Packaging & Containers", "name": "Nilörngruppen AB", "ticker": "NIL-B.ST"},
    {"category": "Security & Protection Services", "name": "Careium AB (Publ)", "ticker": "CARE.ST"},
    {"category": "Real Estate Services", "name": "K2A Knaust & Andersson Fastigheter AB (publ)", "ticker": "K2A-B.ST"},
    {"category": "Software - Application", "name": "Generic Sweden AB", "ticker": "GENI.ST"},
    {"category": "Education & Training Services", "name": "Cedergrenska AB (publ)", "ticker": "CEDER.ST"},
    {"category": "Biotechnology", "name": "FluoGuide A/S", "ticker": "FLUO.ST"},
    {"category": "Steel", "name": "BE Group AB (publ)", "ticker": "BEGR.ST"},
    {"category": "Paper & Paper Products", "name": "Arctic Paper S.A.", "ticker": "ARP.ST"},
    {"category": "Communication Equipment", "name": "Alcadon Group AB (publ)", "ticker": "ALCA.ST"},
    {"category": "Information Technology Services", "name": "White Pearl Technology Group AB", "ticker": "WPTG-B.ST"},
    {"category": "Packaged Foods", "name": "Premium Snacks Nordic AB (publ)", "ticker": "SNX.ST"},
    {"category": "Other Precious Metals & Mining", "name": "Grangex AB", "ticker": "GRANGX.ST"},
    {"category": "Consumer Electronics", "name": "Kjell Group AB (publ)", "ticker": "KJELL.ST"},
    {"category": "Leisure", "name": "Actic Group AB (publ)", "ticker": "ATIC.ST"},
    {"category": "Medical Devices", "name": "Bactiguard Holding AB (publ)", "ticker": "BACTI-B.ST"},
    {"category": "Software - Application", "name": "Opter AB (publ)", "ticker": "OPTER.ST"},
    {"category": "Medical Devices", "name": "Ortoma AB (publ)", "ticker": "ORT-B.ST"},
    {"category": "Software - Application", "name": "Upsales Technology AB (publ)", "ticker": "UPSALE.ST"},
    {"category": "Software - Application", "name": "Done.ai Group AB", "ticker": "DONE.ST"},
    {"category": "Aerospace & Defense", "name": "AAC Clyde Space AB (publ)", "ticker": "AAC.ST"},
    {"category": "Building Products & Equipment", "name": "Concejo AB (publ)", "ticker": "CNCJO-B.ST"},
    {"category": "Credit Services", "name": "Qliro AB (publ)", "ticker": "QLIRO.ST"},
    {"category": "Asset Management", "name": "Boho Group AB (publ)", "ticker": "BOHO.ST"},
    {"category": "Communication Equipment", "name": "KebNi AB (publ)", "ticker": "KEBNI-B.ST"},
    {"category": "Medical Devices", "name": "Q-linea AB (publ)", "ticker": "QLINEA.ST"},
    {"category": "Software - Infrastructure", "name": "Freja eID Group AB (publ)", "ticker": "FREJA.ST"},
    {"category": "Biotechnology", "name": "Corline Biomedical AB", "ticker": "CLBIO.ST"},
    {"category": "Engineering & Construction", "name": "Wall to Wall Group AB", "ticker": "WTW-A.ST"},
    {"category": "Communication Equipment", "name": "Gapwaves AB (publ)", "ticker": "GAPW-B.ST"},
    {"category": "Real Estate Services", "name": "Solnaberg Property AB (publ)", "ticker": "SOLNA.ST"},
    {"category": "Engineering & Construction", "name": "Wästbygg Gruppen AB (publ)", "ticker": "WBGR-B.ST"},
    {"category": "Software - Application", "name": "Sleep Cycle AB (publ)", "ticker": "SLEEP.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Enzymatica AB (publ)", "ticker": "ENZY.ST"},
    {"category": "Aerospace & Defense", "name": "AVTECH Sweden AB (publ)", "ticker": "AVT-B.ST"},
    {"category": "Gold", "name": "Botnia Gold AB (publ)", "ticker": "BOTX.ST"},
    {"category": "Textile Manufacturing", "name": "Duroc AB (publ)", "ticker": "DURC-B.ST"},
    {"category": "Electronic Components", "name": "Unibap Space Solutions AB (publ)", "ticker": "UNIBAP.ST"},
    {"category": "Real Estate - Development", "name": "Titania Holding AB (publ)", "ticker": "TITA-B.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Moberg Pharma AB (publ)", "ticker": "MOB.ST"},
    {"category": "Residential Construction", "name": "Balco Group AB", "ticker": "BALCO.ST"},
    {"category": "Recreational Vehicles", "name": "Nimbus Group AB (Publ)", "ticker": "BOAT.ST"},
    {"category": "Advertising Agencies", "name": "Adtraction Group AB", "ticker": "ADTR.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Sensys Gatso Group AB (publ)", "ticker": "SGG.ST"},
    {"category": "Engineering & Construction", "name": "Infrea AB", "ticker": "INFREA.ST"},
    {"category": "Advertising Agencies", "name": "TradeDoubler AB (publ)", "ticker": "TRAD.ST"},
    {"category": "Asset Management", "name": "NAXS AB (publ)", "ticker": "NAXS.ST"},
    {"category": "Biotechnology", "name": "Magle Chemoswed Holding AB (publ)", "ticker": "MAGLE.ST"},
    {"category": "Capital Markets", "name": "K33 AB (publ)", "ticker": "K33.ST"},
    {"category": "Software - Infrastructure", "name": "4C Group AB (publ)", "ticker": "4C.ST"},
    {"category": "Leisure", "name": "Profoto Holding AB (publ)", "ticker": "PRFO.ST"},
    {"category": "Information Technology Services", "name": "B3 Consulting Group AB (publ)", "ticker": "B3.ST"},
    {"category": "Medical Devices", "name": "Mentice AB (publ)", "ticker": "MNTC.ST"},
    {"category": "Biotechnology", "name": "Ascelia Pharma AB (publ)", "ticker": "ACE.ST"},
    {"category": "Utilities - Renewable", "name": "Minesto AB (publ)", "ticker": "MINEST.ST"},
    {"category": "Other Industrial Metals & Mining", "name": "Nordic Iron Ore AB (publ)", "ticker": "NIO.ST"},
    {"category": "Communication Equipment", "name": "Maven Wireless Sweden AB (Publ)", "ticker": "MAVEN.ST"},
    {"category": "Asset Management", "name": "Navigo Invest AB (publ)", "ticker": "NAVIGO-STAM.ST"},
    {"category": "Pollution & Treatment Controls", "name": "QleanAir AB (publ)", "ticker": "QAIR.ST"},
    {"category": "Computer Hardware", "name": "Tobii AB (publ)", "ticker": "TOBII.ST"},
    {"category": "Staffing & Employment Services", "name": "Dedicare AB (publ)", "ticker": "DEDI.ST"},
    {"category": "Telecom Services", "name": "Transtema Group AB", "ticker": "TRANS.ST"},
    {"category": "Information Technology Services", "name": "mySafety Group AB", "ticker": "SAFETY-B.ST"},
    {"category": "Asset Management", "name": "Athanase Innovation AB (publ)", "ticker": "ATIN.ST"},
    {"category": "Metal Fabrication", "name": "AGES Industri AB (publ)", "ticker": "AGES-B.ST"},
    {"category": "Furnishings, Fixtures & Appliances", "name": "Online Brands Nordic AB (publ)", "ticker": "OBAB.ST"},
    {"category": "Information Technology Services", "name": "Avensia AB (publ)", "ticker": "AVEN.ST"},
    {"category": "Internet Content & Information", "name": "Eniro Group AB (publ)", "ticker": "ENRO.ST"},
    {"category": "Computer Hardware", "name": "Freemelt Holding AB (publ)", "ticker": "FREEM.ST"},
    {"category": "Biotechnology", "name": "Intervacc AB (publ)", "ticker": "IVACC.ST"},
    {"category": "Medical Devices", "name": "Acarix AB (publ)", "ticker": "ACARIX.ST"},
    {"category": "Software - Infrastructure", "name": "Teneo AI AB (publ)", "ticker": "TENEO.ST"},
    {"category": "Specialty Chemicals", "name": "Polygiene Group AB", "ticker": "POLYG.ST"},
    {"category": "Asset Management", "name": "Seafire AB (publ)", "ticker": "SEAF.ST"},
    {"category": "Biotechnology", "name": "Mendus AB (publ)", "ticker": "IMMU.ST"},
    {"category": "Software - Infrastructure", "name": "Binero Group AB (publ)", "ticker": "BINERO.ST"},
    {"category": "Solar", "name": "SolTech Energy Sweden AB (publ)", "ticker": "SOLT.ST"},
    {"category": "Household & Personal Products", "name": "Candles Scandinavia AB (publ)", "ticker": "CANDLE-B.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Nanexa AB (publ)", "ticker": "NANEXA.ST"},
    {"category": "Biotechnology", "name": "Elicera Therapeutics AB (publ)", "ticker": "ELIC.ST"},
    {"category": "Communication Equipment", "name": "Waystream Holding AB (publ)", "ticker": "WAYS.ST"},
    {"category": "Staffing & Employment Services", "name": "Calviks AB (publ)", "ticker": "CALVIK.ST"},
    {"category": "Staffing & Employment Services", "name": "Ogunsen AB (publ)", "ticker": "OGUN-B.ST"},
    {"category": "Furnishings, Fixtures & Appliances", "name": "Lammhults Design Group AB (publ)", "ticker": "LAMM-B.ST"},
    {"category": "Semiconductors", "name": "BeammWave AB (publ)", "ticker": "BEAMMW-B.ST"},
    {"category": "Aerospace & Defense", "name": "OXE Marine AB (publ)", "ticker": "OXE.ST"},
    {"category": "Specialty Retail", "name": "Elon AB (publ)", "ticker": "ELON.ST"},
    {"category": "Software - Application", "name": "Litium AB (publ)", "ticker": "LITI.ST"},
    {"category": "Health Information Services", "name": "Physitrack PLC", "ticker": "PTRK.ST"},
    {"category": "Specialty Chemicals", "name": "Nexam Chemical Holding AB (publ)", "ticker": "NEXAM.ST"},
    {"category": "Farm Products", "name": "Agtira AB", "ticker": "AGTIRA-B.ST"},
    {"category": "Real Estate - Diversified", "name": "Acrinova AB (publ)", "ticker": "ACRI-B.ST"},
    {"category": "Real Estate - Diversified", "name": "Acrinova AB (publ)", "ticker": "ACRI-A.ST"},
    {"category": "Leisure", "name": "Unlimited Travel Group UTG AB (publ)", "ticker": "UTG.ST"},
    {"category": "Real Estate Services", "name": "Bonäsudden Holding AB (publ)", "ticker": "BONAS.ST"},
    {"category": "Software - Application", "name": "Crunchfish AB (publ)", "ticker": "CFISH.ST"},
    {"category": "Biotechnology", "name": "Lipum AB (publ)", "ticker": "LIPUM.ST"},
    {"category": "Software - Application", "name": "Greater Than AB", "ticker": "GREAT.ST"},
    {"category": "Biotechnology", "name": "AlzeCure Pharma AB (publ)", "ticker": "ALZCUR.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "MAG Interactive AB (publ)", "ticker": "MAGI.ST"},
    {"category": "Medical Devices", "name": "Promimic AB (publ)", "ticker": "PRO.ST"},
    {"category": "Medical Instruments & Supplies", "name": "iZafe Group AB (publ)", "ticker": "IZAFE-B.ST"},
    {"category": "Electronics & Computer Distribution", "name": "Malmbergs Elektriska AB (publ)", "ticker": "MEAB-B.ST"},
    {"category": "Communication Equipment", "name": "TagMaster AB (publ)", "ticker": "TAGM-B.ST"},
    {"category": "Medical Devices", "name": "Integrum AB (publ)", "ticker": "INTEG-B.ST"},
    {"category": "Medical Devices", "name": "Boule Diagnostics AB (publ)", "ticker": "BOUL.ST"},
    {"category": "Software - Application", "name": "CodeMill AB (publ)", "ticker": "CDMIL.ST"},
    {"category": "Medical Devices", "name": "Clinical Laserthermia Systems AB (publ)", "ticker": "CLS-B.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Enorama Pharma AB (publ)", "ticker": "ERMA.ST"},
    {"category": "Biotechnology", "name": "Karolinska Development AB (publ)", "ticker": "KDEV.ST"},
    {"category": "Real Estate Services", "name": "Link Prop Investment AB (publ)", "ticker": "LINKAB.ST"},
    {"category": "Specialty Business Services", "name": "ScandBook Holding AB (publ)", "ticker": "SBOK.ST"},
    {"category": "Other Industrial Metals & Mining", "name": "Arctic Minerals AB (publ)", "ticker": "ARCT.ST"},
    {"category": "Biotechnology", "name": "Xbrane Biopharma AB (publ)", "ticker": "XBRANE.ST"},
    {"category": "Specialty Industrial Machinery", "name": "OptiCept Technologies AB (publ)", "ticker": "OPTI.ST"},
    {"category": "Security & Protection Services", "name": "Precise Biometrics AB (publ)", "ticker": "PREC.ST"},
    {"category": "Diagnostics & Research", "name": "Immunovia AB (publ)", "ticker": "IMMNOV.ST"},
    {"category": "Biotechnology", "name": "Medivir AB (publ)", "ticker": "MVIR.ST"},
    {"category": "Biotechnology", "name": "Initiator Pharma A/S", "ticker": "INIT.ST"},
    {"category": "Engineering & Construction", "name": "Hifab Group AB (publ)", "ticker": "HIFA-B.ST"},
    {"category": "Staffing & Employment Services", "name": "PION Group AB (publ)", "ticker": "PION-B.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Rolling Optics Holding AB (publ)", "ticker": "RO.ST"},
    {"category": "Other Industrial Metals & Mining", "name": "District Metals Corp.", "ticker": "DMXSE-SDB.ST"},
    {"category": "Biotechnology", "name": "IRLAB Therapeutics AB (publ)", "ticker": "IRLAB-A.ST"},
    {"category": "Biotechnology", "name": "Isofol Medical AB (publ)", "ticker": "ISOFOL.ST"},
    {"category": "Software - Application", "name": "Modelon AB (publ)", "ticker": "MODEL.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Starbreeze AB (publ)", "ticker": "STAR-B.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Starbreeze AB (publ)", "ticker": "STAR-A.ST"},
    {"category": "Software - Application", "name": "Safeture AB (publ)", "ticker": "SFTR.ST"},
    {"category": "Information Technology Services", "name": "Precio Fishbone AB (publ)", "ticker": "PRCO-B.ST"},
    {"category": "Solar", "name": "Gigasun AB (publ)", "ticker": "GIGA.ST"},
    {"category": "Engineering & Construction", "name": "Netel Holding AB (publ)", "ticker": "NETEL.ST"},
    {"category": "Diagnostics & Research", "name": "SenzaGen AB", "ticker": "SENZA.ST"},
    {"category": "Specialty Chemicals", "name": "OrganoClick AB (publ)", "ticker": "ORGC.ST"},
    {"category": "Biotechnology", "name": "Xintela AB (publ)", "ticker": "XINT.ST"},
    {"category": "Software - Application", "name": "oodash Group AB (publ)", "ticker": "OODA.ST"},
    {"category": "Gambling", "name": "Acroud AB (publ)", "ticker": "ACROUD.ST"},
    {"category": "Biotechnology", "name": "Annexin Pharmaceuticals AB (publ)", "ticker": "ANNX.ST"},
    {"category": "Waste Management", "name": "Norditek Group AB (publ)", "ticker": "NOTEK.ST"},
    {"category": "Leisure", "name": "Söder Sportfiske AB", "ticker": "SODER.ST"},
    {"category": "Specialty Business Services", "name": "Drillcon AB (publ)", "ticker": "DRIL.ST"},
    {"category": "Chemicals", "name": "Serstech AB", "ticker": "SERT.ST"},
    {"category": "Specialty Industrial Machinery", "name": "SeaTwirl AB (publ)", "ticker": "STW.ST"},
    {"category": "Software - Infrastructure", "name": "Alpcot Holding AB (publ)", "ticker": "ALPCOT-B.ST"},
    {"category": "Software - Application", "name": "Checkin.Com Group AB (publ)", "ticker": "CHECK.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Fingerprint Cards AB (publ)", "ticker": "FING-B.ST"},
    {"category": "Farm & Heavy Construction Machinery", "name": "Lyckegård Group AB (publ)", "ticker": "LYGRD.ST"},
    {"category": "Capital Markets", "name": "Havsfrun Investment AB (publ)", "ticker": "HAV-B.ST"},
    {"category": "Internet Content & Information", "name": "Catena Media plc", "ticker": "CTM.ST"},
    {"category": "Biotechnology", "name": "Alzinova AB (publ)", "ticker": "ALZ.ST"},
    {"category": "Entertainment", "name": "Moment Group AB", "ticker": "MOMENT.ST"},
    {"category": "Gambling", "name": "Gaming Corps AB (publ)", "ticker": "GCOR.ST"},
    {"category": "Specialty Chemicals", "name": "aXichem AB", "ticker": "AXIC-A.ST"},
    {"category": "Medical Instruments & Supplies", "name": "Ortivus AB (publ)", "ticker": "ORTI-B.ST"},
    {"category": "Medical Instruments & Supplies", "name": "Ortivus AB (publ)", "ticker": "ORTI-A.ST"},
    {"category": "Biotechnology", "name": "Biovica International AB (publ)", "ticker": "BIOVIC-B.ST"},
    {"category": "Beverages - Wineries & Distilleries", "name": "High Coast Distillery AB (Publ)", "ticker": "HIGHCO-B.ST"},
    {"category": "Software - Application", "name": "Terranet AB", "ticker": "TERRNT-B.ST"},
    {"category": "Other Precious Metals & Mining", "name": "First Nordic Metals Corp.", "ticker": "FNMC-SDB.ST"},
    {"category": "Software - Infrastructure", "name": "Westpay AB", "ticker": "WPAY.ST"},
    {"category": "Electronics & Computer Distribution", "name": "DistIT AB (publ)", "ticker": "DIST.ST"},
    {"category": "Specialty Industrial Machinery", "name": "FlexQube AB (publ)", "ticker": "FLEXQ.ST"},
    {"category": "Medical Devices", "name": "BrainCool AB (publ)", "ticker": "BRAIN.ST"},
    {"category": "Software - Application", "name": "Klimator AB (publ)", "ticker": "KLIMAT.ST"},
    {"category": "Packaging & Containers", "name": "Bong AB (publ)", "ticker": "BONG.ST"},
    {"category": "Utilities - Renewable", "name": "Climeon AB (publ)", "ticker": "CLIME-B.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Flexion Mobile Plc", "ticker": "FLEXM.ST"},
    {"category": "Packaged Foods", "name": "New Nordic Healthbrands AB (publ)", "ticker": "NNH.ST"},
    {"category": "Software - Application", "name": "DevPort AB (publ)", "ticker": "DEVP-B.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Impact Coatings AB (publ)", "ticker": "IMPC.ST"},
    {"category": "Household & Personal Products", "name": "Clemondo Group AB (publ)", "ticker": "CLEM.ST"},
    {"category": "Asset Management", "name": "Vo2 Cap Holding AB (publ)", "ticker": "VO2.ST"},
    {"category": "Medical Devices", "name": "Nosa Plugs AB", "ticker": "NOSA.ST"},
    {"category": "Internet Retail", "name": "Vuxen Group AB", "ticker": "VUXEN.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Vivesto AB", "ticker": "VIVE.ST"},
    {"category": "Software - Application", "name": "eEducation Albert AB (publ)", "ticker": "ALBERT.ST"},
    {"category": "Security & Protection Services", "name": "Nordic LEVEL Group AB (publ.)", "ticker": "LEVEL.ST"},
    {"category": "Metal Fabrication", "name": "Cell Impact AB (publ)", "ticker": "CI.ST"},
    {"category": "Conglomerates", "name": "Stockwik Förvaltning AB (publ)", "ticker": "STWK.ST"},
    {"category": "Software - Application", "name": "Safello Group AB (publ)", "ticker": "SFL.ST"},
    {"category": "Specialty Business Services", "name": "Nepa AB (publ)", "ticker": "NEPA.ST"},
    {"category": "Waste Management", "name": "Axolot Solutions Holding AB (publ)", "ticker": "AXOLOT.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Klaria Pharma Holding AB (publ.)", "ticker": "KLAR.ST"},
    {"category": "Medical Devices", "name": "Neola Medical AB (publ)", "ticker": "NEOLA.ST"},
    {"category": "Consumer Electronics", "name": "Image Systems AB", "ticker": "IS.ST"},
    {"category": "Electrical Equipment & Parts", "name": "Ferroamp AB (publ)", "ticker": "FERRO.ST"},
    {"category": "Leisure", "name": "Uswe Sports AB (publ)", "ticker": "USWE.ST"},
    {"category": "Medical Devices", "name": "Arcoma AB", "ticker": "ARCOMA.ST"},
    {"category": "Biotechnology", "name": "Biosergen AB (publ)", "ticker": "BIOSGN.ST"},
    {"category": "Consulting Services", "name": "Vimab Group AB (publ)", "ticker": "VIMAB.ST"},
    {"category": "Biotechnology", "name": "Nanologica AB (publ)", "ticker": "NICA.ST"},
    {"category": "Medical Devices", "name": "SciBase Holding AB (publ)", "ticker": "SCIB.ST"},
    {"category": "Diagnostics & Research", "name": "IDL Diagnostics AB (publ)", "ticker": "IDLDX.ST"},
    {"category": "Security & Protection Services", "name": "Tempest Security AB (publ)", "ticker": "TSEC.ST"},
    {"category": "Medical Devices", "name": "SpectraCure AB (publ)", "ticker": "SPEC.ST"},
    {"category": "Biotechnology", "name": "Pila Pharma AB (publ)", "ticker": "PILA.ST"},
    {"category": "Biotechnology", "name": "Active Biotech AB (publ)", "ticker": "ACTI.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Guideline Geo AB (publ)", "ticker": "GGEO.ST"},
    {"category": "Staffing & Employment Services", "name": "Wise Group AB (publ)", "ticker": "WISE.ST"},
    {"category": "Computer Hardware", "name": "Realfiction Holding AB (publ)", "ticker": "REALFI.ST"},
    {"category": "Biotechnology", "name": "Scandinavian ChemoTech AB (publ)", "ticker": "CMOTEC-B.ST"},
    {"category": "Education & Training Services", "name": "Tellusgruppen AB (publ)", "ticker": "TELLUS.ST"},
    {"category": "Biotechnology", "name": "Nanoform Finland Oyj", "ticker": "NANOFS.ST"},
    {"category": "Pollution & Treatment Controls", "name": "Bawat Water Technologies AB", "ticker": "BAWAT.ST"},
    {"category": "Advertising Agencies", "name": "Raketech Group Holding PLC", "ticker": "RAKE.ST"},
    {"category": "Biotechnology", "name": "NextCell Pharma AB", "ticker": "NXTCL.ST"},
    {"category": "Other Precious Metals & Mining", "name": "Lucara Diamond Corp.", "ticker": "LUC.ST"},
    {"category": "Building Products & Equipment", "name": "ES Energy Save Holding AB (publ)", "ticker": "ESGR-B.ST"},
    {"category": "Software - Application", "name": "Bambuser AB (publ)", "ticker": "BUSER.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Thunderful Group AB", "ticker": "THUNDR.ST"},
    {"category": "Telecom Services", "name": "TalkPool AG", "ticker": "TALK.ST"},
    {"category": "Medical Devices", "name": "Iconovo AB (publ)", "ticker": "ICO.ST"},
    {"category": "Medical Devices", "name": "Luxbright AB (publ)", "ticker": "LXB.ST"},
    {"category": "Waste Management", "name": "Bioextrax AB (publ)", "ticker": "BIOEX.ST"},
    {"category": "Biotechnology", "name": "OncoZenge AB (publ)", "ticker": "ONCOZ.ST"},
    {"category": "Biotechnology", "name": "Spago Nanomedical AB (publ)", "ticker": "SPAGO.ST"},
    {"category": "Software - Application", "name": "Kentima Holding AB (publ)", "ticker": "KENH.ST"},
    {"category": "Communication Equipment", "name": "InCoax Networks AB (publ)", "ticker": "INCOAX.ST"},
    {"category": "Medical Devices", "name": "Scandinavian Real Heart AB (Publ)", "ticker": "HEART.ST"},
    {"category": "Biotechnology", "name": "Sprint Bioscience AB (publ)", "ticker": "SPRINT.ST"},
    {"category": "Specialty Industrial Machinery", "name": "BoMill AB (publ)", "ticker": "BOMILL.ST"},
    {"category": "Internet Retail", "name": "New Bubbleroom Sweden AB (publ)", "ticker": "BBROOM.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Fragbite Group AB (publ)", "ticker": "FRAG.ST"},
    {"category": "Electrical Equipment & Parts", "name": "Heliospectra AB (publ)", "ticker": "HELIO.ST"},
    {"category": "Chemicals", "name": "XP Chemistries AB (publ)", "ticker": "XPC.ST"},
    {"category": "Internet Retail", "name": "Desenio Group AB (publ)", "ticker": "DSNO.ST"},
    {"category": "Pollution & Treatment Controls", "name": "Saxlund Group AB (publ)", "ticker": "SAXG.ST"},
    {"category": "Health Information Services", "name": "Kontigo Care AB (publ)", "ticker": "KONT.ST"},
    {"category": "Biotechnology", "name": "Simris Group AB (PUBL)", "ticker": "SIMRIS-B.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Gasporox AB (publ)", "ticker": "GPX.ST"},
    {"category": "Software - Infrastructure", "name": "Sonetel AB (publ)", "ticker": "SONE.ST"},
    {"category": "Engineering & Construction", "name": "Hexicon AB (publ)", "ticker": "HEXI.ST"},
    {"category": "Oil & Gas E&P", "name": "Africa Energy Corp.", "ticker": "AEC.ST"},
    {"category": "Consulting Services", "name": "Brilliant Future AB (publ)", "ticker": "BRILL.ST"},
    {"category": "Biotechnology", "name": "Lipigon Pharmaceuticals AB (publ)", "ticker": "LPGO.ST"},
    {"category": "Other Industrial Metals & Mining", "name": "Leading Edge Materials Corp.", "ticker": "LEMSE.ST"},
    {"category": "Software - Application", "name": "Flowscape Technology AB (publ)", "ticker": "FLOWS.ST"},
    {"category": "Computer Hardware", "name": "JLT Mobile Computers AB (publ)", "ticker": "JLT.ST"},
    {"category": "Software - Application", "name": "SpectrumOne AB (publ)", "ticker": "SPEONE.ST"},
    {"category": "Real Estate Services", "name": "Aktiebolaget Fastator (publ)", "ticker": "FASTAT.ST"},
    {"category": "Biotechnology", "name": "AcouSort AB (publ)", "ticker": "ACOU.ST"},
    {"category": "Software - Infrastructure", "name": "Anoto Group AB (publ)", "ticker": "ANOT.ST"},
    {"category": "Security & Protection Services", "name": "Irisity AB (publ)", "ticker": "IRIS.ST"},
    {"category": "Asset Management", "name": "First Venture Sweden AB (publ)", "ticker": "FIRST-B.ST"},
    {"category": "Software - Application", "name": "Divio Technologies AB (publ)", "ticker": "DIVIO-B.ST"},
    {"category": "Biotechnology", "name": "ExpreS2ion Biotech Holding AB (publ)", "ticker": "EXPRS2.ST"},
    {"category": "Medical Devices", "name": "ScandiDos AB (publ)", "ticker": "SDOS.ST"},
    {"category": "Biotechnology", "name": "Alligator Bioscience AB (publ)", "ticker": "ATORX.ST"},
    {"category": "Biotechnology", "name": "Modus Therapeutics Holding AB (publ)", "ticker": "MODTX.ST"},
    {"category": "Software - Application", "name": "Ranplan Group AB", "ticker": "RPLAN.ST"},
    {"category": "Medical Devices", "name": "Episurf Medical AB (publ)", "ticker": "EPIS-B.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Newbury Pharmaceuticals AB (publ)", "ticker": "NEWBRY.ST"},
    {"category": "Asset Management", "name": "Lärkberget AB (publ)", "ticker": "LARK.ST"},
    {"category": "Internet Retail", "name": "Sweden Buyersclub AB", "ticker": "BUY.ST"},
    {"category": "Specialty Chemicals", "name": "Svenska Aerogel Holding AB (publ)", "ticker": "AERO.ST"},
    {"category": "Consumer Electronics", "name": "Northbaze Group AB (publ)", "ticker": "NBZ.ST"},
    {"category": "Specialty Chemicals", "name": "Tribox Group AB (publ)", "ticker": "TRIBO-B.ST"},
    {"category": "Internet Content & Information", "name": "Tourn International AB (publ)", "ticker": "TOURN.ST"},
    {"category": "Utilities - Renewable", "name": "Dlaboratory Sweden AB (publ)", "ticker": "DLAB.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Scout Gaming Group AB (publ)", "ticker": "SCOUT.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Nitro Games Oyj", "ticker": "NITRO.ST"},
    {"category": "Health Information Services", "name": "Aino Health AB (publ)", "ticker": "AINO.ST"},
    {"category": "Household & Personal Products", "name": "LifeClean International AB (publ)", "ticker": "LCLEAN.ST"},
    {"category": "Software - Application", "name": "Zaplox AB", "ticker": "ZAPLOX.ST"},
    {"category": "Entertainment", "name": "Goodbye Kansas Group AB (publ)", "ticker": "GBK.ST"},
    {"category": "Waste Management", "name": "Mashup Ireland AB", "ticker": "MASHUP.ST"},
    {"category": "Waste Management", "name": "CirChem AB (publ)", "ticker": "CIRCHE.ST"},
    {"category": "Software - Application", "name": "Diadrom Holding AB (publ)", "ticker": "DIAH.ST"},
    {"category": "Software - Application", "name": "M.O.B.A. Network AB", "ticker": "MOBA.ST"},
    {"category": "Agricultural Inputs", "name": "Cinis Fertilizer AB (publ)", "ticker": "CINIS.ST"},
    {"category": "Biotechnology", "name": "2cureX AB (publ)", "ticker": "2CUREX.ST"},
    {"category": "Tobacco", "name": "Nicoccino Holding AB (publ)", "ticker": "NICO.ST"},
    {"category": "Biotechnology", "name": "Guard Therapeutics International AB (publ)", "ticker": "GUARD.ST"},
    {"category": "Software - Application", "name": "Loyal Solutions A/S", "ticker": "LOYAL.ST"},
    {"category": "Building Materials", "name": "Kakel Max AB (publ)", "ticker": "KAKEL.ST"},
    {"category": "Real Estate Services", "name": "Tessin Nordic Holding AB (publ)", "ticker": "TESSIN.ST"},
    {"category": "Staffing & Employment Services", "name": "NetJobs Group AB (publ)", "ticker": "NJOB.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Qiiwi Games AB (publ)", "ticker": "QIIWI.ST"},
    {"category": "Metal Fabrication", "name": "Nordic Flanges Group AB (publ)", "ticker": "NFGAB.ST"},
    {"category": "Staffing & Employment Services", "name": "Hedera Group AB (publ)", "ticker": "HEGR.ST"},
    {"category": "Medical Devices", "name": "Qlife Holding AB (publ)", "ticker": "QLIFE.ST"},
    {"category": "Biotechnology", "name": "Novakand Pharma AB (publ)", "ticker": "NOVKAN.ST"},
    {"category": "Medical Devices", "name": "Magnasense AB", "ticker": "MAGNA.ST"},
    {"category": "Medical Devices", "name": "Perpetua Medical AB (publ)", "ticker": "PERP-B.ST"},
    {"category": "Software - Application", "name": "Qlucore AB (publ)", "ticker": "QCORE.ST"},
    {"category": "Metal Fabrication", "name": "Precomp Solutions AB (publ)", "ticker": "PCOM-B.ST"},
    {"category": "Asset Management", "name": "NanoCap Group AB (publ)", "ticker": "NANOC-B.ST"},
    {"category": "Auto Manufacturers", "name": "Clean Motion AB (publ)", "ticker": "CLEMO.ST"},
    {"category": "Diagnostics & Research", "name": "Prostatype Genomics AB (publ)", "ticker": "PROGEN.ST"},
    {"category": "Internet Content & Information", "name": "BrightBid Group AB (publ)", "ticker": "BRIGHT.ST"},
    {"category": "Biotechnology", "name": "Fluicell AB (publ)", "ticker": "FLUI.ST"},
    {"category": "Information Technology Services", "name": "Fram Skandinavien AB (publ)", "ticker": "FRAM-B.ST"},
    {"category": "Software - Application", "name": "Sileon AB (publ)", "ticker": "SILEON.ST"},
    {"category": "Specialty Industrial Machinery", "name": "Mantex AB (publ)", "ticker": "MANTEX.ST"},
    {"category": "Internet Retail", "name": "Refine Group AB (publ)", "ticker": "REFINE.ST"},
    {"category": "Software - Application", "name": "Spotr Group AB", "ticker": "SPOTR.ST"},
    {"category": "Biotechnology", "name": "Stayble Therapeutics AB (publ)", "ticker": "STABL.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Insplorion AB (publ)", "ticker": "INSP.ST"},
    {"category": "Beverages - Wineries & Distilleries", "name": "Arctic Blue Beverages AB (publ)", "ticker": "ARCTIC.ST"},
    {"category": "Entertainment", "name": "Mavshack AB (publ)", "ticker": "MAV.ST"},
    {"category": "Software - Application", "name": "XMReality AB (publ)", "ticker": "XMR.ST"},
    {"category": "Medical Devices", "name": "Chordate Medical Holding AB (publ)", "ticker": "CMH-PREF.ST"},
    {"category": "Medical Devices", "name": "Chordate Medical Holding AB (publ)", "ticker": "CMH.ST"},
    {"category": "Household & Personal Products", "name": "LN Future Invest AB (publ)", "ticker": "LNFI.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Maximum Entertainment AB", "ticker": "MAXENT-B.ST"},
    {"category": "Information Technology Services", "name": "Wyld Networks AB (publ)", "ticker": "WYLD.ST"},
    {"category": "Medical Instruments & Supplies", "name": "S2Medical AB (publ)", "ticker": "S2M.ST"},
    {"category": "Lodging", "name": "Hotel Fast SSE AB (publ)", "ticker": "HOTEL.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Gabather AB (publ)", "ticker": "GABA.ST"},
    {"category": "Biotechnology", "name": "LIDDS AB (publ)", "ticker": "LIDDS.ST"},
    {"category": "Biotechnology", "name": "Quia Pharma AB (publ)", "ticker": "QUIA.ST"},
    {"category": "Software - Infrastructure", "name": "Cyber Security 1 AB (publ)", "ticker": "CYB1.ST"},
    {"category": "Information Technology Services", "name": "Ortelius International AB", "ticker": "ORTIN.ST"},
    {"category": "Software - Application", "name": "Enersize Oyj", "ticker": "ENERS.ST"},
    {"category": "Information Technology Services", "name": "Qlosr Group AB (publ)", "ticker": "QLOSR-B.ST"},
    {"category": "Apparel Manufacturing", "name": "Björn Borg AB (publ)", "ticker": "BORG.ST"},
    {"category": "Asset Management", "name": "Brock Milton Capital AB (publ)", "ticker": "BMC.ST"},
    {"category": "Software - Application", "name": "ChargePanel AB (publ)", "ticker": "CHARGE.ST"},
    {"category": "Drug Manufacturers - Specialty & Generic", "name": "Cinclus Pharma Holding AB (publ)", "ticker": "CINPHA.ST"},
    {"category": "Software - Application", "name": "Compodium International AB (publ)", "ticker": "COMPDM.ST"},
    {"category": "Asset Management", "name": "Effnetplattformen Holding AB (publ)", "ticker": "EFFH.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "EMB Mission Bound AB (publ)", "ticker": "EMB.ST"},
    {"category": "Mortgage Finance", "name": "Enity Holding AB (publ)", "ticker": "ENITY.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Envar Holding AB (publ)", "ticker": "ENVAR.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "FSport AB (publ)", "ticker": "FSPORT.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "GiG Software p.l.c.", "ticker": "GIG-SDB.ST"},
    {"category": "Beverages - Wineries & Distilleries", "name": "Hernö Gin AB (publ)", "ticker": "HERNO-B.ST"},
    {"category": "Asset Management", "name": "Hilbert Group AB (publ)", "ticker": "HILB-B.ST"},
    {"category": "Electronic Gaming & Multimedia", "name": "Kinda Brave Entertainment Group Ab (Publ)", "ticker": "BRAVE.ST"},
    {"category": "Asset Management", "name": "MTI Investment AB (publ)", "ticker": "MTI.ST"},
    {"category": "Biotechnology", "name": "NanoEcho AB (publ)", "ticker": "NANECH.ST"},
    {"category": "Software - Application", "name": "Neovici Holding AB (publ)", "ticker": "NEO-B.ST"},
    {"category": "Information Technology Services", "name": "Observit AB", "ticker": "OBSE.ST"},
    {"category": "Engineering & Construction", "name": "Qben Infra AB (publ)", "ticker": "QBEN.ST"},
    {"category": "Scientific & Technical Instruments", "name": "Qualisys Holding AB (publ)", "ticker": "QSYS.ST"},
    {"category": "Scientific & Technical Instruments", "name": "RanLOS AB (publ)", "ticker": "RLOS-B.ST"},
    {"category": "Credit Services", "name": "SaveLend Group AB (publ)", "ticker": "YIELD.ST"},
    {"category": "Security & Protection Services", "name": "Sibek AB (publ)", "ticker": "SIBEK.ST"},
    {"category": "Engineering & Construction", "name": "Terranor Group AB (publ)", "ticker": "TERNOR.ST"},
    {"category": "Asset Management", "name": "Västra Hamnen Corporate Finance AB (publ)", "ticker": "VH.ST"},
    {"category": "Asset Management", "name": "Webrock Ventures AB", "ticker": "WRV.ST"},
]
# Sort by category then name for a structured dropdown
TICKER_DATA.sort(key=lambda x: (x['category'], x['name']))

# Pre-made categories
PREDEFINED_CATEGORIES = {
    "ALL": [item['ticker'] for item in TICKER_DATA],
    "OMXS30": ["ABB.ST", "ADDT-B.ST", "ALFA.ST", "ASSS-B.ST", "AZN.ST", "ATCO-A.ST", "BOL.ST", "EPI-A.ST", "EQT.ST", "ERIC-B.ST", "ESSITY-B.ST", "EVO.ST", "HM-B.ST", "SHB-A.ST", "HEXA-B.ST", "INDU-C.ST", "INVE-B.ST", "LIFCO-B.ST", "NIBE-B.ST", "NDA-SE.ST", "SAAB-B.ST", "SAND.ST", "SCA-B.ST", "SEB-A.ST", "SKA-B.ST", "SKF-B.ST", "SWED-A.ST", "TEL2-B.ST", "TELIA.ST", "VOLV-B.ST"]
    # Can add more categories like "DAX", "S&P 500" here later
}

# -----------------------------------------------------------------------------
# 1. SMART WALLET (With Memory for Trailing Stops)
# -----------------------------------------------------------------------------

class Wallet:
    def __init__(self, cash: float):
        self.cash = cash
        # Structure: 
        # { 'TICKER': {'amount': int, 'avg_price': float, 'max_price': float} }
        self.stocks = {} 

    def get_holding(self, ticker):
        return self.stocks.get(ticker, {'amount': 0, 'avg_price': 0.0, 'max_price': 0.0})

    def update_high_watermark(self, ticker, current_price):
        """Tracks the highest price seen since we bought the stock (for trailing stops)."""
        if ticker in self.stocks:
            if current_price > self.stocks[ticker]['max_price']:
                self.stocks[ticker]['max_price'] = current_price

    def buy(self, ticker, price, amount):
        if amount <= 0 or self.cash < (price * amount): return
        
        cost = price * amount
        self.cash -= cost
        
        current = self.get_holding(ticker)
        old_amount = current['amount']
        old_avg = current['avg_price']
        
        new_amount = old_amount + amount
        
        # Calculate Weighted Average Price
        if old_amount > 0:
            total_val = (old_amount * old_avg) + cost
            new_avg = total_val / new_amount
        else:
            new_avg = price
            
        # If new position, max_price is current price. 
        # If adding to position, we generally keep the old max_price or reset. 
        # For simplicity: keep old max unless current is higher.
        new_max = max(current['max_price'], price) if old_amount > 0 else price

        self.stocks[ticker] = {
            'amount': new_amount, 
            'avg_price': new_avg, 
            'max_price': new_max
        }

    def sell(self, ticker, price, amount):
        current = self.get_holding(ticker)
        if current['amount'] >= amount and amount > 0:
            self.cash += price * amount
            remaining = current['amount'] - amount
            
            if remaining <= 0:
                if ticker in self.stocks: del self.stocks[ticker]
            else:
                self.stocks[ticker]['amount'] = remaining
                # We do NOT reset avg_price or max_price on partial sells usually

    def get_total_market_value(self, current_prices):
        val = self.cash
        for ticker, data in self.stocks.items():
            price = current_prices.get(ticker, data['avg_price'])
            val += data['amount'] * price
        return val
    
    def get_total_buy_value(self):
        val = 0.0
        for ticker, data in self.stocks.items():
            val += data['amount'] * data['avg_price']
        val = val + self.cash
        return val 

# -----------------------------------------------------------------------------
# 2. DATA ENGINE
# -----------------------------------------------------------------------------

@st.cache_data
def get_data(tickers, start, end):
    if not tickers: return pd.DataFrame()
    df = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=False)
    return df

def pre_calculate_indicators(df, indicators):
    is_multi = isinstance(df.columns, pd.MultiIndex)
    if is_multi:
        tickers = df.columns.get_level_values(1).unique()
        data_map = {}
        for ticker in tickers:
            sub_df = df.xs(ticker, axis=1, level=1).copy()
            data_map[ticker] = apply_indicators_single(sub_df, indicators)
        return data_map
    else:
        ticker = df.columns[0] if len(df.columns) > 0 else "Asset"
        return {ticker: apply_indicators_single(df.copy(), indicators)}

def apply_indicators_single(df, indicators):
    df.columns = [c.lower() for c in df.columns]
    for ind in indicators:
        try:
            if "sma" in ind:
                window = int(ind.split("_")[1])
                df[ind] = df['close'].rolling(window=window).mean()
            elif "ema" in ind:
                window = int(ind.split("_")[1])
                df[ind] = df['close'].ewm(span=window).mean()
            elif "rsi" in ind:
                window = int(ind.split("_")[1])
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
                rs = gain / loss
                df[ind] = 100 - (100 / (1 + rs))
            elif "bb" in ind:
                window = int(ind.split("_")[1])
                df[f'bb_middle_{window}'] = df['close'].rolling(window=window).mean()
                df[f'bb_std_{window}'] = df['close'].rolling(window=window).std()
                df[f'bb_upper_{window}'] = df[f'bb_middle_{window}'] + (df[f'bb_std_{window}'] * 2)
                df[f'bb_lower_{window}'] = df[f'bb_middle_{window}'] - (df[f'bb_std_{window}'] * 2)
            elif "macd" in ind:
                # Default MACD uses 12-period EMA, 26-period EMA, and 9-period EMA for signal line
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                df['macd'] = exp1 - exp2
                df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
                df['macd_histogram'] = df['macd'] - df['signal_line']
            elif "stoch" in ind: # Stochastic Oscillator
                window = int(ind.split("_")[1])
                df['lowest_low'] = df['low'].rolling(window=window).min()
                df['highest_high'] = df['high'].rolling(window=window).max()
                df[ind] = ((df['close'] - df['lowest_low']) / (df['highest_high'] - df['lowest_low'])) * 100
        except: pass
    return df.fillna(0)

# -----------------------------------------------------------------------------
# 3. LOGIC EVALUATOR
# -----------------------------------------------------------------------------

def evaluate_condition(row, condition_str, wallet_context):
    """
    Merges Market Data (row) with Wallet Data (wallet_context)
    to allow rules like 'close < avg_price'.
    """
    try:
        # Combine row data (Open, Close, SMA) with Wallet data (avg_price, cash)
        combined_context = {**row.to_dict(), **wallet_context}
        return eval(condition_str, {"__builtins__": None}, combined_context)
    except Exception as e:
        # st.write(f"Debug Error in rule: {condition_str} -> {e}") # Uncomment for debugging
        return False

# -----------------------------------------------------------------------------
# 4. UI & SIMULATION
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Pro Strategy Builder", layout="centered")
st.title("🧠 Pro Strategy Builder")
# --- HELP SECTION ---
with st.expander("📚 Variable Cheat Sheet (Click to Expand)"):
    st.markdown("""
    **Market Variables:**
    * `close`, `open`, `high`, `low`
    * `sma_50`, `rsi_14` (Whatever you defined)
    * `bb_middle_20`, `bb_upper_20`, `bb_lower_20` (for Bollinger Bands)
    * `macd`, `signal_line`, `macd_histogram` (for MACD)
    * `stoch_14` (for Stochastic Oscillator)
    **Wallet Variables (Crucial for Stoploss/Martingale):**
    * `avg_price`: Your average buy price for this stock.
    * `pct_profit`: Your current P/L % (e.g., -0.05 is -5%).
    * `max_price`: The highest price reached since you bought (for Trailing Stop).
    * `cash`: Total available cash.
    
    **Examples:**
    * **Stop Loss 5%:** `pct_profit < -0.05`
    * **Take Profit 20%:** `pct_profit > 0.20`
    * **Trailing Stop 10%:** `close < max_price * 0.90`
    * **Martingale (Buy More on dip):** `pct_profit < -0.10` (Put this in BUY condition)
    """)
    st.markdown("""
    **Bollinger Bands Example:**
    * **Buy:** `close < bb_lower_20`
    * **Sell:** `close > bb_upper_20`""")

# --- INPUT SECTION ---
st.header("1. Setup")

# Create a list of display names for the multiselect, including category
ticker_display_list = [f"[{item['category']}] {item['name']} ({item['ticker']})" for item in TICKER_DATA]

# Create a mapping from display name to ticker
ticker_map = {f"[{item['category']}] {item['name']} ({item['ticker']})": item['ticker'] for item in TICKER_DATA}

# Create a reverse map from ticker to display name to easily find display names
ticker_to_display_map = {v: k for k, v in ticker_map.items()}

# --- Category Selection ---
category_options = ["Custom"] + list(PREDEFINED_CATEGORIES.keys())
selected_category = st.selectbox("Ticker Category", category_options)

default_selection = []
if selected_category == "Custom":
    # Default to Volvo if custom is selected, for a better user experience
    default_ticker = "VOLV-B.ST"
    default_display = [item for item in ticker_display_list if default_ticker in item]
    default_selection = default_display
else:
    # Get tickers for the selected category and map them to their display names
    category_tickers = PREDEFINED_CATEGORIES[selected_category]
    default_selection = [ticker_to_display_map[ticker] for ticker in category_tickers if ticker in ticker_to_display_map]

tickers_display_input = st.multiselect("Tickers", ticker_display_list, default=default_selection)

# Convert selected display names back to tickers
tickers_input = [ticker_map[display] for display in tickers_display_input]

start_d = st.date_input("Start", pd.to_datetime("2022-01-01"))
end_d = st.date_input("End", pd.to_datetime("2023-12-01"))

# Typed Input for Cash
cash = st.number_input("Initial Cash", value=100000, step=1000)

st.divider()
st.header("2. Indicators")
indicators_raw = st.text_area("Define Indicators", "sma_50, sma_200, rsi_14, bb_20, macd, stoch_14")
indicator_list = [x.strip() for x in indicators_raw.split(",") if x.strip()]

st.divider()
st.header("3. Buy Logic & Sizing")

# Initialize session state with the new 'type' field
if 'buy_rules' not in st.session_state:
    st.session_state.buy_rules = [
        {"type": "% Cash", "cond": "low < bb_lower_20", "size": 2.0},
        {"type": "% Position", "cond": "pct_profit < -0.05", "size": 200.0} 
    ]

# Function to add a new blank rule
def add_rule():
    st.session_state.buy_rules.append({"type": "% Cash", "cond": "pct_profit < -0.05", "size": 5.0})

# Function to remove the last rule
def remove_rule():
    if len(st.session_state.buy_rules) > 0:
        st.session_state.buy_rules.pop()

# Display the Rules as a List with 4 Columns
for i, rule in enumerate(st.session_state.buy_rules):
    # Columns: [Index] [Type] [Condition] [Size]
    c1, c2, c3, c4 = st.columns([0.1, 0.25, 0.45, 0.2])
    
    with c1:
        st.markdown(f"**#{i+1}**")
    with c2:
        # Ensure 'type' exists (backward compatibility fix)
        if 'type' not in rule: rule['type'] = "% Cash"
        rule['type'] = st.selectbox("Type", ["% Cash", "% Position"], key=f"rule_t_{i}", label_visibility="collapsed")
    with c3:
        rule['cond'] = st.text_input("Condition", rule['cond'], key=f"rule_c_{i}", label_visibility="collapsed", placeholder="e.g. pct_profit < -0.10")
    with c4:
        rule['size'] = st.number_input("Size %", value=rule['size'], key=f"rule_s_{i}", label_visibility="collapsed")

# Buttons
b1, b2 = st.columns(2)
b1.button("➕ Add Rule", on_click=add_rule)
b2.button("➖ Remove Last", on_click=remove_rule)

st.divider()
st.header("4. Sell Logic")
st.markdown("Use variables: `pct_profit`, `avg_price`, `max_price`")

# Initialize session state for sell rules
if 'sell_rules' not in st.session_state:
    st.session_state.sell_rules = [
        {"cond": "pct_profit > 0.05", "size": 100.0},
        {"cond": "pct_profit < -0.10", "size": 100.0}
    ]

# Function to add a new blank sell rule
def add_sell_rule():
    st.session_state.sell_rules.append({"cond": "pct_profit > 0.05", "size": 100.0})

# Function to remove the last sell rule
def remove_sell_rule():
    if len(st.session_state.sell_rules) > 0:
        st.session_state.sell_rules.pop()

# Display the Sell Rules as a List with 3 Columns
for i, rule in enumerate(st.session_state.sell_rules):
    c1, c2, c3 = st.columns([0.1, 0.6, 0.3])
    
    with c1:
        st.markdown(f"**#{i+1}**")
    with c2:
        rule['cond'] = st.text_input("Condition", rule['cond'], key=f"sell_rule_c_{i}", label_visibility="collapsed", placeholder="e.g. pct_profit > 0.05")
    with c3:
        rule['size'] = st.number_input("Size %", value=rule['size'], key=f"sell_rule_s_{i}", label_visibility="collapsed")

# Buttons for sell rules
b_sell1, b_sell2 = st.columns(2)
b_sell1.button("➕ Add Sell Rule", on_click=add_sell_rule)
b_sell2.button("➖ Remove Last Sell Rule", on_click=remove_sell_rule)


run = st.button("Run Simulation", type="primary")


# --- MAIN ---
if run:
    st.divider()
    st.header("📊 Simulation Results")
    if not tickers_input:
        st.error("Select tickers.")
    else:
        with st.spinner("Processing..."):
            raw_df = get_data(tickers_input, start_d, end_d)
            
        if raw_df.empty:
            st.error("No data.")
        else:
            # Pre-calc indicators
            data_map = pre_calculate_indicators(raw_df, indicator_list)
            
            wallet = Wallet(cash)
            history = []
            close_prices_history = []
            common_index = data_map[tickers_input[0]].index
            
            progress = st.progress(0)
            
            for i, date in enumerate(common_index):
                if i % 50 == 0: progress.progress(i / len(common_index))
                
                current_prices_snapshot = {}

                for ticker in tickers_input:
                    df = data_map[ticker]
                    if date not in df.index: continue
                    
                    row = df.loc[date]
                    current_price = row['close']
                    current_prices_snapshot[ticker] = current_price
                    
                    # 1. UPDATE TRACKING (High Watermark)
                    wallet.update_high_watermark(ticker, current_price)
                    
                    # 2. PREPARE CONTEXT VARIABLES
                    holding = wallet.get_holding(ticker)
                    avg_p = holding['avg_price']
                    max_p = holding['max_price']
                    amt = holding['amount']
                    
                    # Calculate profit percentage (avoid division by zero)
                    if avg_p > 0:
                        pct_profit = (current_price - avg_p) / avg_p
                    else:
                        pct_profit = 0.0
                    
                    context = {
                        "avg_price": avg_p,
                        "max_price": max_p,
                        "pct_profit": pct_profit,
                        "cash": wallet.cash,
                        "amount": amt
                    }

                    # 3. EVALUATE BUY
                    if current_price <= 0: continue
                    
                    # --- NEW LOGIC START ---
                    amount_to_buy = 0
                    rule_matched = False

                    # 1. Check Dynamic Rules
                    for rule in st.session_state.buy_rules:
                        if evaluate_condition(row, rule['cond'], context):
                            
                            size_val = rule['size'] / 100.0
                            
                            if rule['type'] == "% Position":
                                # BUY BASED ON EXISTING AMOUNT
                                # If Size is 100%, we buy exactly what we currently have (Doubling down)
                                current_amt = context['amount']
                                if current_amt > 0:
                                    amount_to_buy = int(current_amt * size_val)
                                else:
                                    # Fallback: If we have 0 shares, % Position implies 0 buy. 
                                    # Force a tiny cash buy or skip? Let's skip to be safe.
                                    amount_to_buy = 0 
                            else:
                                # BUY BASED ON CASH (Standard)
                                amount_to_buy = int((wallet.cash * size_val) / current_price)
                            
                            rule_matched = True
                            break # Stop after first match

                    # 2. If no rule matched, do nothing.
                    if not rule_matched:
                        amount_to_buy = 0
                    # --- NEW LOGIC END ---

                    if amount_to_buy > 0:
                        wallet.buy(ticker, current_price, amount_to_buy)
                    
                    # 4. EVALUATE SELL
                    if amt > 0:
                        amount_to_sell = 0
                        
                        # Check Dynamic Sell Rules
                        for rule in st.session_state.sell_rules:
                            if evaluate_condition(row, rule['cond'], context):
                                size_val = rule['size'] / 100.0
                                amount_to_sell = int(amt * size_val)
                                break # Stop after first match

                        # If no rule matched, or if the rule resulted in 0 amount to sell,
                        # we could add a default sell logic here if desired.
                        # For now, if no rule matches, amount_to_sell remains 0.

                        # Ensure we don't try to sell more than we own
                        amount_to_sell = min(amount_to_sell, amt)

                        if amount_to_sell > 0:
                            wallet.sell(ticker, current_price, amount_to_sell)

                # Log
                total_m_val = wallet.get_total_market_value(current_prices_snapshot)
                total_b_val = wallet.get_total_buy_value()
                history.append({"Date": date, "Portfolio Market Value": total_m_val, "Portfolio Buy Value": total_b_val, "Cash": wallet.cash})

                
            
            progress.empty()
            
            # VISUALIZATION
            res_df = pd.DataFrame(history).set_index("Date")
            final_v = res_df["Portfolio Buy Value"].iloc[-1]

            st.metric("Final Purchase Value", f"{final_v:,.2f} SEK", delta=f"{final_v - cash:,.2f}")
            st.metric("Final Market Value", f"{total_m_val:,.2f} SEK", delta=f"{total_m_val - cash:,.2f}")
            st.metric("Final Cash Left", f"{wallet.cash:,.2f} SEK", delta=f"{wallet.cash - cash:,.2f}")


            # --- CHART 1: Portfolio Value (Scaled) ---
            # We need to "melt" the dataframe to put multiple lines on one Altair chart
            chart_data = res_df.reset_index().melt('Date', value_vars=["Portfolio Market Value", "Portfolio Buy Value"])
            
            c1 = alt.Chart(chart_data).mark_line().encode(
                x='Date',
                # zero=False is the key setting here:
                y=alt.Y('value', title='Value (SEK)', scale=alt.Scale(zero=False)), 
                color='variable',
                tooltip=['Date', 'variable', 'value']
            ).interactive() # Makes it zoomable/pannable
            
            st.altair_chart(c1)

            # --- CHART 2: Stock Price (Scaled) ---
            if len(tickers_input) <= 1:
                aaa = []
                for i in range(len(raw_df.index)):
                    aaa.append({"Date": raw_df.index[i], "Price": raw_df['Close'][tickers_input[0]].iloc[i]})
                aaa_df = pd.DataFrame(aaa)
                
                c2 = alt.Chart(aaa_df).mark_line().encode(
                    x='Date',
                    y=alt.Y('Price', scale=alt.Scale(zero=False)), # Scales to Min/Max
                    tooltip=['Date', 'Price']
                ).interactive()
                st.altair_chart(c2)
            else:
                # For multiple tickers, we need to melt the DataFrame to plot all 'Close' prices
                # The raw_df already has the 'Close' prices for all tickers
                chart_data_multi_ticker = raw_df['Close'].reset_index().melt('Date', var_name='Ticker', value_name='Close')
            
                # Calculate percentage change from the first close price for each ticker
                # This requires grouping by ticker and then applying a transform
                chart_data_multi_ticker['Initial_Close'] = chart_data_multi_ticker.groupby('Ticker')['Close'].transform('first')
                chart_data_multi_ticker['Percentage_Change'] = (chart_data_multi_ticker['Close'] / chart_data_multi_ticker['Initial_Close'] - 1) * 100

                # Plotting Percentage_Change instead of Close
                c2 = alt.Chart(chart_data_multi_ticker).mark_line().encode(x='Date', 
                                                                       y=alt.Y('Percentage_Change', title='Price Movement (%)', scale=alt.Scale(zero=False)),
                    color='Ticker',
                tooltip=['Date', 'Ticker', 
                         alt.Tooltip('Close', format='.2f', title='Close Price'), 
                         alt.Tooltip('Percentage_Change', format='.2f', title='Movement %')
                        ]
                ).interactive()
                st.altair_chart(c2)

            # --- CHART 3: Cash --- 

            c3 = alt.Chart(res_df.reset_index()).mark_line().encode(
                x='Date',
                y=alt.Y('Cash', scale=alt.Scale(zero=False)),
                tooltip=['Date', 'Cash']
            ).interactive()
            st.altair_chart(c3)

            if wallet.stocks:
                st.subheader("Ending Portfolio")
                
                portfolio_data = []
                for ticker, data in wallet.stocks.items():
                    current_price = current_prices_snapshot.get(ticker, data['avg_price']) # Use last known price
                    market_value = data['amount'] * current_price
                    buy_value = data['amount'] * data['avg_price']
                    profit_loss = market_value - buy_value
                    pct_profit_loss = (profit_loss / buy_value) * 100 if buy_value > 0 else 0

                    portfolio_data.append({
                        "Ticker": ticker,
                        "Amount": data['amount'],
                        "Avg Price": f"{data['avg_price']:.2f}",
                        "Current Price": f"{current_price:.2f}",
                        "Market Value": f"{market_value:,.2f}",
                        "P/L": f"{profit_loss:,.2f}",
                        "P/L %": f"{pct_profit_loss:.2f}%"
                    })
                
                portfolio_df = pd.DataFrame(portfolio_data)
                st.dataframe(portfolio_df, hide_index=True)