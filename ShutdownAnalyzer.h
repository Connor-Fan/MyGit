/** @file
  Register names for PCH PMC device

  Conventions:

  - Register definition format:
    Prefix_[GenerationName]_[ComponentName]_SubsystemName_RegisterSpace_RegisterName
  - Prefix:
    Definitions beginning with "R_" are registers
    Definitions beginning with "B_" are bits within registers
    Definitions beginning with "V_" are meaningful values within the bits
    Definitions beginning with "S_" are register size
    Definitions beginning with "N_" are the bit position
  - [GenerationName]:
    Three letter acronym of the generation is used (e.g. SKL,KBL,CNL etc.).
    Register name without GenerationName applies to all generations.
  - [ComponentName]:
    This field indicates the component name that the register belongs to (e.g. PCH, SA etc.)
    Register name without ComponentName applies to all components.
    Register that is specific to -H denoted by "_PCH_H_" in component name.
    Register that is specific to -LP denoted by "_PCH_LP_" in component name.
  - SubsystemName:
    This field indicates the subsystem name of the component that the register belongs to
    (e.g. PCIE, USB, SATA, GPIO, PMC etc.).
  - RegisterSpace:
    MEM - MMIO space register of subsystem.
    IO  - IO space register of subsystem.
    PCR - Private configuration register of subsystem.
    CFG - PCI configuration space register of subsystem.
  - RegisterName:
    Full register name.

@copyright
  INTEL CONFIDENTIAL
  Copyright 1999 - 2022 Intel Corporation.

  The source code contained or described herein and all documents related to the
  source code ("Material") are owned by Intel Corporation or its suppliers or
  licensors. Title to the Material remains with Intel Corporation or its suppliers
  and licensors. The Material may contain trade secrets and proprietary and
  confidential information of Intel Corporation and its suppliers and licensors,
  and is protected by worldwide copyright and trade secret laws and treaty
  provisions. No part of the Material may be used, copied, reproduced, modified,
  published, uploaded, posted, transmitted, distributed, or disclosed in any way
  without Intel's prior express written permission.

  No license under any patent, copyright, trade secret or other intellectual
  property right is granted to or conferred upon you by disclosure or delivery
  of the Materials, either expressly, by implication, inducement, estoppel or
  otherwise. Any license under such intellectual property rights must be
  express and approved by Intel in writing.

  Unless otherwise agreed by Intel in writing, you may not remove or alter
  this notice or any other notice embedded in Materials by Intel or
  Intel's suppliers or licensors in any way.

  This file contains an 'Intel Peripheral Driver' and is uniquely identified as
  "Intel Reference Module" and is licensed for Intel CPUs and chipsets under
  the terms of your license agreement with Intel or your vendor. This file may
  be modified by the user, subject to additional terms of the license agreement.

@par Specification
**/
#ifndef _SHUTDOWN_ANALYZER_H_
#define _SHUTDOWN_ANALYZER_H_

#define PCH_PWRM_BASE_ADDRESS                                    0xFE000000      ///< PMC MBAR MMIO base address

#define R_PMC_PWRM_GBLRST_CAUSE0                                 0x1924          ///< Global Reset Causes 0
#define B_PMC_PWRM_GBLRST_CAUSE0_IOE_GRST_TRIGGER                BIT31           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_IOE_SOC_PMC_TYPE_8_GRST_TRIGGER BIT31           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_ESE_GBLRST_REQ                  BIT30           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_IOE_THRM                        BIT28           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_GFX_THRM                        BIT26           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_COMPUTE_THRM                    BIT25           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PMC_IROM_PARITY                 BIT23           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PMC_SRAM_UNC_ERR                BIT22           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_OCWDT_NOICC                     BIT19           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_ME_UNC_ERR                      BIT17           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_ISH                             BIT13           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_SYSPWR_FLR                      BIT12           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PCHPWR_FLR                      BIT11           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PMC_FW                          BIT10           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_ME_WDT                          BIT9            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PMC_WDT                         BIT8            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_MEGBL                           BIT6            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_SOCN_THRM                       BIT5            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_ME_PBO                          BIT4            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_SOCS_THRM                       BIT3            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PMC_UNC_ERR                     BIT2            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_PBO                             BIT1            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_SECURE_POLICY_ERR               BIT0            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE0_IOE_SOC_PMC_TYPE_7_GRST_TRIGGER BIT0            ///< 

#define R_PMC_PWRM_GBLRST_CAUSE1                                 0X1928          ///< Global Reset Causes 1
#define B_PMC_PWRM_GBLRST_CAUSE1_SLP_LVL_RSP_ERR                 BIT14           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_BSCAN_MODE                      BIT13           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_LPM_FW_ERR                      BIT12           ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_ESPI_TYPE8                      BIT9            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_ESPI_TYPE7                      BIT8            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_PMC_3STRIKE                     BIT4            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_HOST_RST_PROM                   BIT2            ///< 
#define B_PMC_PWRM_GBLRST_CAUSE1_HOST_RESET_TIMEOUT              BIT0            ///< 

#define R_PMC_PWRM_HPR_CAUSE0                                    0x192C          ///< Host Partition Reset Causes
#define B_PMC_PWRM_HPR_CAUSE0_ESPI_HRWPC                         BIT17           ///< 
#define B_PMC_PWRM_HPR_CAUSE0_ESPI_HRWOPC                        BIT16           ///< 
#define B_PMC_PWRM_HPR_CAUSE0_HSMB_HRPC                          BIT13           ///< 
#define B_PMC_PWRM_HPR_CAUSE0_HSMB_HR                            BIT12           ///< 
#define B_PMC_PWRM_HPR_CAUSE0_MI_HRPD                            BIT10           ///< 
#define B_PMC_PWRM_HPR_CAUSE0_MI_HRPC                            BIT9            ///< 
#define B_PMC_PWRM_HPR_CAUSE0_MI_HR                              BIT8            ///< 
#define B_PMC_PWRM_HPR_CAUSE0_TCO_WDT                            BIT6            ///< 
#define B_PMC_PWRM_HPR_CAUSE0_SYSRST_ES                          BIT2            ///< 
#define B_PMC_PWRM_HPR_CAUSE0_CF9_ES                             BIT1            ///< 

#endif
