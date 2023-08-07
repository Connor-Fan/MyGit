/** @file
  This sample application bases on HelloWorld PCD setting
  to print "UEFI Hello World!" to the UEFI Console.

  Copyright (c) 2006 - 2018, Intel Corporation. All rights reserved.<BR>
  SPDX-License-Identifier: BSD-2-Clause-Patent

**/

#include <Uefi.h>
#include <Library/BaseLib.h>
#include <Library/UefiLib.h>
#include <Library/UefiApplicationEntryPoint.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/IoLib.h>
#include <Protocol/ShellParameters.h>
#include "ShutdownAnalyzer.h"

//
// String token ID of help message text.
// Shell supports to find help message in the resource section of an application image if
// .MAN file is not found. This global variable is added to make build tool recognizes
// that the help string is consumed by user and then build tool will add the string into
// the resource section. Thus the application can use '-?' option to show help message in
// Shell.
//

static UINTN  Argc;
static CHAR16 **Argv;

/**

  This function parse application ARG.

  @return Status
**/
static
EFI_STATUS
GetArg (
  VOID
  )
{
  EFI_STATUS                    Status;
  EFI_SHELL_PARAMETERS_PROTOCOL *ShellParameters;

  Status = gBS->HandleProtocol (
                  gImageHandle,
                  &gEfiShellParametersProtocolGuid,
                  (VOID**)&ShellParameters
                  );
  if (EFI_ERROR(Status)) {
    return Status;
  }

  Argc = ShellParameters->Argc;
  Argv = ShellParameters->Argv;
  return EFI_SUCCESS;
}

/**
   Display Usage and Help information.
**/
VOID
ShowHelp (
  )
{
  Print(L"Usage: myapp [-h | -H | -? | -MTL | -mtl | -LNL | -lnl | -RPL | -rpl]\n");
  Print(L"Options:\n");
  Print(L"  -h    : Display this help message\n");
  Print(L"  -H    : Display this help message\n");
  Print(L"  -?    : Display this help message\n");
  Print(L"  -MTL  : Print the corresponding message for each set bit (CPU Model: MTL)\n");
  Print(L"  -mtl  : Print the corresponding message for each set bit (CPU Model: MTL)\n");
  Print(L"  -LNL  : Print the corresponding message for each set bit (CPU Model: LNL)\n");
  Print(L"  -lnl  : Print the corresponding message for each set bit (CPU Model: LNL)\n");
  Print(L"  -RPL  : Print the corresponding message for each set bit (CPU Model: RPL)\n");
  Print(L"  -rpl  : Print the corresponding message for each set bit (CPU Model: RPL)\n");
  Print(L"\n");
  Print(L"This application displays information about unexpected shutdown causes based on the specified CPU model.\n");
  Print(L"By providing the appropriate CPU model option, you can see which bits in the global reset causes register were set when an unexpected shutdown occurred.\n");
  Print(L"This information is derived from the Intel External Design Specification (EDS) for kit number 657165.\n");
  Print(L"The EDS provides detailed information about the global reset causes and their meanings for different CPU models.\n");
  Print(L"This tool can be useful for diagnosing and troubleshooting unexpected shutdown issues on systems based on Intel CPUs.\n");
}

/**
   .
**/
EFI_STATUS
EFIAPI
GlobalResetCauses0 (
  VOID
  )
{
  //EFI_STATUS Status;
  UINT8 Index;
  UINT32 Data = 0; // Default value if MMIO32 read fails
  
  // Read data from MMIO32 address
  Data = MmioRead32 (PCH_PWRM_BASE_ADDRESS + R_PMC_PWRM_GBLRST_CAUSE0);
  
  Print(L"Global Reset Causes 0 (GBLRST_CAUSE0): 0x%08x\n", Data);

  // Use for loop to check each bit and print the corresponding message
  for (Index = 0; Index < 32; Index++) {
    if (Data & (1 << Index)) {
      switch (1 << Index) {
        case B_PMC_PWRM_GBLRST_CAUSE0_IOE_​GRST_​TRIGGER:
      //case B_PMC_PWRM_GBLRST_CAUSE0_IOE_​SOC_​PMC_​TYPE_​8_​GRST_​TRIGGER:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by an IOE global reset trigger.\n", Index);
		  Print(L"Bit %d: If bit is set to 1, the last global reset was caused by an IOE PMC type 8 global reset trigger.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_ESE_​GBLRST_​REQ:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by a security global reset request.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_IOE_​THRM:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by IOE thermal.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_GFX_​THRM:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by graphics thermal.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_COMPUTE_​THRM:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by compute tile thermal.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PMC_​IROM_​PARITY:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by PMC ROM parity.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PMC_​SRAM_​UNC_​ERR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by PMC SRAM uncorrrectable errors.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_OCWDT_​NOICC:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by over clocking watchdog timer expired.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_ME_​UNC_​ERR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused a CSME uncorrectable error.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_ISH:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by ISH.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_SYSPWR_​FLR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by SYS_​PWROK going low in S0.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PCHPWR_​FLR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by PLT_​PWROK going low in S0.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PMC_​FW:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by PMC FW.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_ME_​WDT:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by CSME watchdog timer expired.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PMC_​WDT:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by PMC watchdog timer expired.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_MEGBL:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by a CSME global reset (with details reflected in GBLRST_​CAUSE1 register).\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_SOCN_​THRM:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by the SoC north tile thermal.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_ME_​PBO:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by CSME power button override.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_SOCS_​THRM:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by the SoC South tile thermal.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PMC_​UNC_​ERR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by a PMC uncorrectable error.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_PBO:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by power button override.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE0_SECURE_​POLICY_​ERR:
      //case B_PMC_PWRM_GBLRST_CAUSE0_IOE_​SOC_​PMC_​TYPE_​7_​GRST_​TRIGGER:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by a security policy error.\n", Index);
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by an IOE PMC type 7 global reset trigger.\n", Index);
          break;

        default:
          Print(L"Bit %d: If bit is set to 1, but its cause is not specified in the Intel EDS (CPU Model: MTL).\n", Index);
          break;
      }
    }
  }
 
  return EFI_SUCCESS;
}

/**
   .
**/
EFI_STATUS
EFIAPI
GlobalResetCauses1 (
  VOID
  )
{
  //EFI_STATUS Status;
  UINT8 Index;
  UINT32 Data = 0; // Default value if MMIO32 read fails
  
  // Read data from MMIO32 address
  Data = MmioRead32 (PCH_PWRM_BASE_ADDRESS + R_PMC_PWRM_GBLRST_CAUSE1);

  Print(L"Global Reset Causes 1 (GBLRST_CAUSE1): 0x%08x\n", Data);

  // Use for loop to check each bit and print the corresponding message
  for (Index = 0; Index < 32; Index++) {
    if (Data & (1 << Index)) {
      switch (1 << Index) {
        case B_PMC_PWRM_GBLRST_CAUSE1_SLP_​LVL_​RSP_​ERR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by power management handshake response failure global reset.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_BSCAN_​MODE:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by BSCAN mode.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_LPM_​FW_​ERR:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by low power mode exit failure.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_ESPI_​TYPE8:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by eSPI type 8.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_ESPI_​TYPE7:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by eSPI type 7.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_PMC_​3STRIKE:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by PMC 3 strike.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_HOST_​RST_​PROM:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by host reset promotion.\n", Index);
          break;

        case B_PMC_PWRM_GBLRST_CAUSE1_HOST_​RESET_​TIMEOUT:
          Print(L"Bit %d: If bit is set to 1, the last global reset was caused by a host reset timeout.\n", Index);
          break;

        default:
          Print(L"Bit %d: If bit is set to 1, but its cause is not specified in the Intel EDS (CPU Model: MTL).\n", Index);
          break;
      }
    }
  }
 
  return EFI_SUCCESS;
}

/**
   .
**/
EFI_STATUS
EFIAPI
HostPartitionResetCauses (
  VOID
  )
{
  //EFI_STATUS Status;
  UINT8 Index;
  UINT32 Data = 0; // Default value if MMIO32 read fails
  
  // Read data from MMIO32 address
  Data = MmioRead32 (PCH_PWRM_BASE_ADDRESS + R_PMC_PWRM_HPR_CAUSE0);

  Print(L"Host Partition Reset Causes (HPR_CAUSE0): 0x%08x\n", Data);

  // Use for loop to check each bit and print the corresponding message
  for (Index = 0; Index < 32; Index++) {
    if (Data & (1 << Index)) {
      switch (1 << Index) {
        case B_PMC_PWRM_HPR_CAUSE0_ESPI_​HRWPC:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by eSPI Host Reset With Power Cycle.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_ESPI_​HRWOPC:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by eSPI Host Reset Without Power Cycle.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_HSMB_​HRPC:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by Host SMBUS Host Reset With Power Cycle.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_HSMB_​HR:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by Host SMBUS Host Reset Without Power Cycle.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_MI_​HRPD:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by ME-Initiated Host Reset With Power Down.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_MI_​HRPC:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by ME-Initiated Host Reset With Power Cycle.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_MI_​HR:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by ME-Initiated Host Reset Without Power Cycle.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_TCO_​WDT:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by Host TCO Watchdog Timer Second Expiration.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_SYSRST_​ES:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by Assertion of the SYS_RESET# pin after the 16 ms HW debounce.\n", Index);
          break;

        case B_PMC_PWRM_HPR_CAUSE0_CF9_​ES:
          Print(L"Bit %d: If bit is set to 1, the last host partition reset was caused by Write to CF9 (Host software writes value 6h or Eh to the CF9 register).\n", Index);
          break;

        default:
          Print(L"Bit %d: If bit is set to 1, but its cause is not specified in the Intel EDS (Host Partition Reset Causes).\n", Index);
          break;
      }
    }
  }
 
  return EFI_SUCCESS;
}

/**
  The user Entry Point for Application. The user code starts with this function
  as the real entry point for the application.

  @param[in] ImageHandle    The firmware allocated handle for the EFI image.
  @param[in] SystemTable    A pointer to the EFI System Table.

  @retval EFI_SUCCESS       The entry point is executed successfully.
  @retval other             Some error occurs when executing this entry point.

**/
EFI_STATUS
EFIAPI
UefiMain (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
  )
{
  // Print app information
  Print (L"\n");
  Print (L"=============================\n");
  Print (L"    MyApp Version 1.0.0\n");
  Print (L"     Author: Kanan Fan\n");
  Print (L"=============================\n");
  Print (L"\n");
  Print (L"Please subscribe to Gawr Guar's YouTube channel!\n");
  Print (L"YT Channel: https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g\n");
  Print (L"\n");
  Print (L"** Important Note **\n");
  Print (L"This application is intended for informational purposes only and should be used with caution.\n");
  Print (L"Before using this tool to diagnose or troubleshoot any issues, please ensure you have a backup of your data.\n");
  Print (L"If you encounter any bugs or unexpected behavior while using this application, please report it to the developer.\n");
  Print (L"Feedback and suggestions are also welcome to improve the application's functionality.\n");
  Print (L"Use this application at your own risk, and the developer is not responsible for any data loss or damages caused by its use.\n");
  Print (L"\n");
  
  EFI_STATUS                    Status;

  //
  // get the command line arguments
  //
  Status = GetArg();
  if (EFI_ERROR(Status)){
    Print (L"The input parameters are not recognized.\n");
    Status = EFI_INVALID_PARAMETER;
    return Status;
  }

  if (Argc > 2){
    Print (L"Too many arguments specified.\n");
    Status = EFI_INVALID_PARAMETER;
    return Status;
  }

  if (Argc == 1){
    Print(L"Error: No input parameter provided. Use '-?' option for help and usage information.\n");
    goto Done;
  }
  
  if ((StrCmp(Argv[1], L"-?") == 0)||(StrCmp(Argv[1], L"-h") == 0)||(StrCmp(Argv[1], L"-H") == 0)){
    ShowHelp ();
    goto Done;
  } else {
    if ((StrCmp(Argv[1], L"-mtl") == 0)||(StrCmp(Argv[1], L"-MTL") == 0)){
      Status = GlobalResetCauses0();
      if (EFI_ERROR(Status)) {
        Print(L"Error: Failed to retrieve Global Reset Causes 0. Error code: %r\n", Status);
        return Status;
      }

      Status = GlobalResetCauses1();
      if (EFI_ERROR(Status)) {
        Print(L"Error: Failed to retrieve Global Reset Causes 1. Error code: %r\n", Status);
        return Status;
      }
	  
	  Status = HostPartitionResetCauses ();
      if (EFI_ERROR(Status)) {
        Print(L"Error: Failed to retrieve Host Partition Reset Causes. Error code: %r\n", Status);
        return Status;
      }
	  
      goto Done;
    } else {
      if (StrStr(Argv[1], L"-") != NULL){
        Print (L"The argument '%s' is invalid.\n", Argv[1]);
        Status = EFI_INVALID_PARAMETER;
        return Status;
      }
    }
  }

Done:

  return EFI_SUCCESS;
}
