# mypy: disable-error-code="empty-body"
from __future__ import annotations
import ctypes
from typing import Literal, TypeAlias
from tinygrad.runtime.support.c import _IO, _IOW, _IOR, _IOWR
from tinygrad.runtime.support import c
FEATURE_PWR_DOMAIN_e: dict[int, str] = {(FEATURE_PWR_ALL:=0): 'FEATURE_PWR_ALL', (FEATURE_PWR_S5:=1): 'FEATURE_PWR_S5', (FEATURE_PWR_BACO:=2): 'FEATURE_PWR_BACO', (FEATURE_PWR_SOC:=3): 'FEATURE_PWR_SOC', (FEATURE_PWR_GFX:=4): 'FEATURE_PWR_GFX', (FEATURE_PWR_DOMAIN_COUNT:=5): 'FEATURE_PWR_DOMAIN_COUNT'}
@c.record
class EccInfo_t(c.Struct):
  SIZE = 24
  mca_umc_status: int
  mca_umc_addr: int
  ce_count_lo_chip: int
  ce_count_hi_chip: int
  eccPadding: int
uint64_t: TypeAlias = ctypes.c_uint64
uint16_t: TypeAlias = ctypes.c_uint16
uint32_t: TypeAlias = ctypes.c_uint32
EccInfo_t.register_fields([('mca_umc_status', uint64_t, 0), ('mca_umc_addr', uint64_t, 8), ('ce_count_lo_chip', uint16_t, 16), ('ce_count_hi_chip', uint16_t, 18), ('eccPadding', uint32_t, 20)])
@c.record
class EccInfoTable_t(c.Struct):
  SIZE = 384
  EccInfo: c.Array[EccInfo_t, Literal[16]]
EccInfoTable_t.register_fields([('EccInfo', c.Array[EccInfo_t, Literal[16]], 0)])
DRAM_BIT_WIDTH_TYPE_e: dict[int, str] = {(DRAM_BIT_WIDTH_DISABLED:=0): 'DRAM_BIT_WIDTH_DISABLED', (DRAM_BIT_WIDTH_X_8:=1): 'DRAM_BIT_WIDTH_X_8', (DRAM_BIT_WIDTH_X_16:=2): 'DRAM_BIT_WIDTH_X_16', (DRAM_BIT_WIDTH_X_32:=3): 'DRAM_BIT_WIDTH_X_32', (DRAM_BIT_WIDTH_X_64:=4): 'DRAM_BIT_WIDTH_X_64', (DRAM_BIT_WIDTH_X_128:=5): 'DRAM_BIT_WIDTH_X_128', (DRAM_BIT_WIDTH_COUNT:=6): 'DRAM_BIT_WIDTH_COUNT'}
I2cControllerPort_e: dict[int, str] = {(I2C_CONTROLLER_PORT_0:=0): 'I2C_CONTROLLER_PORT_0', (I2C_CONTROLLER_PORT_1:=1): 'I2C_CONTROLLER_PORT_1', (I2C_CONTROLLER_PORT_COUNT:=2): 'I2C_CONTROLLER_PORT_COUNT'}
I2cControllerName_e: dict[int, str] = {(I2C_CONTROLLER_NAME_VR_GFX:=0): 'I2C_CONTROLLER_NAME_VR_GFX', (I2C_CONTROLLER_NAME_VR_SOC:=1): 'I2C_CONTROLLER_NAME_VR_SOC', (I2C_CONTROLLER_NAME_VR_VDDCI:=2): 'I2C_CONTROLLER_NAME_VR_VDDCI', (I2C_CONTROLLER_NAME_VR_MVDD:=3): 'I2C_CONTROLLER_NAME_VR_MVDD', (I2C_CONTROLLER_NAME_LIQUID0:=4): 'I2C_CONTROLLER_NAME_LIQUID0', (I2C_CONTROLLER_NAME_LIQUID1:=5): 'I2C_CONTROLLER_NAME_LIQUID1', (I2C_CONTROLLER_NAME_PLX:=6): 'I2C_CONTROLLER_NAME_PLX', (I2C_CONTROLLER_NAME_OTHER:=7): 'I2C_CONTROLLER_NAME_OTHER', (I2C_CONTROLLER_NAME_COUNT:=8): 'I2C_CONTROLLER_NAME_COUNT'}
I2cControllerThrottler_e: dict[int, str] = {(I2C_CONTROLLER_THROTTLER_TYPE_NONE:=0): 'I2C_CONTROLLER_THROTTLER_TYPE_NONE', (I2C_CONTROLLER_THROTTLER_VR_GFX:=1): 'I2C_CONTROLLER_THROTTLER_VR_GFX', (I2C_CONTROLLER_THROTTLER_VR_SOC:=2): 'I2C_CONTROLLER_THROTTLER_VR_SOC', (I2C_CONTROLLER_THROTTLER_VR_VDDCI:=3): 'I2C_CONTROLLER_THROTTLER_VR_VDDCI', (I2C_CONTROLLER_THROTTLER_VR_MVDD:=4): 'I2C_CONTROLLER_THROTTLER_VR_MVDD', (I2C_CONTROLLER_THROTTLER_LIQUID0:=5): 'I2C_CONTROLLER_THROTTLER_LIQUID0', (I2C_CONTROLLER_THROTTLER_LIQUID1:=6): 'I2C_CONTROLLER_THROTTLER_LIQUID1', (I2C_CONTROLLER_THROTTLER_PLX:=7): 'I2C_CONTROLLER_THROTTLER_PLX', (I2C_CONTROLLER_THROTTLER_INA3221:=8): 'I2C_CONTROLLER_THROTTLER_INA3221', (I2C_CONTROLLER_THROTTLER_COUNT:=9): 'I2C_CONTROLLER_THROTTLER_COUNT'}
I2cControllerProtocol_e: dict[int, str] = {(I2C_CONTROLLER_PROTOCOL_VR_XPDE132G5:=0): 'I2C_CONTROLLER_PROTOCOL_VR_XPDE132G5', (I2C_CONTROLLER_PROTOCOL_VR_IR35217:=1): 'I2C_CONTROLLER_PROTOCOL_VR_IR35217', (I2C_CONTROLLER_PROTOCOL_TMP_TMP102A:=2): 'I2C_CONTROLLER_PROTOCOL_TMP_TMP102A', (I2C_CONTROLLER_PROTOCOL_INA3221:=3): 'I2C_CONTROLLER_PROTOCOL_INA3221', (I2C_CONTROLLER_PROTOCOL_COUNT:=4): 'I2C_CONTROLLER_PROTOCOL_COUNT'}
@c.record
class I2cControllerConfig_t(c.Struct):
  SIZE = 8
  Enabled: int
  Speed: int
  SlaveAddress: int
  ControllerPort: int
  ControllerName: int
  ThermalThrotter: int
  I2cProtocol: int
  PaddingConfig: int
uint8_t: TypeAlias = ctypes.c_ubyte
I2cControllerConfig_t.register_fields([('Enabled', uint8_t, 0), ('Speed', uint8_t, 1), ('SlaveAddress', uint8_t, 2), ('ControllerPort', uint8_t, 3), ('ControllerName', uint8_t, 4), ('ThermalThrotter', uint8_t, 5), ('I2cProtocol', uint8_t, 6), ('PaddingConfig', uint8_t, 7)])
I2cPort_e: dict[int, str] = {(I2C_PORT_SVD_SCL:=0): 'I2C_PORT_SVD_SCL', (I2C_PORT_GPIO:=1): 'I2C_PORT_GPIO'}
I2cSpeed_e: dict[int, str] = {(I2C_SPEED_FAST_50K:=0): 'I2C_SPEED_FAST_50K', (I2C_SPEED_FAST_100K:=1): 'I2C_SPEED_FAST_100K', (I2C_SPEED_FAST_400K:=2): 'I2C_SPEED_FAST_400K', (I2C_SPEED_FAST_PLUS_1M:=3): 'I2C_SPEED_FAST_PLUS_1M', (I2C_SPEED_HIGH_1M:=4): 'I2C_SPEED_HIGH_1M', (I2C_SPEED_HIGH_2M:=5): 'I2C_SPEED_HIGH_2M', (I2C_SPEED_COUNT:=6): 'I2C_SPEED_COUNT'}
I2cCmdType_e: dict[int, str] = {(I2C_CMD_READ:=0): 'I2C_CMD_READ', (I2C_CMD_WRITE:=1): 'I2C_CMD_WRITE', (I2C_CMD_COUNT:=2): 'I2C_CMD_COUNT'}
FanMode_e: dict[int, str] = {(FAN_MODE_AUTO:=0): 'FAN_MODE_AUTO', (FAN_MODE_MANUAL_LINEAR:=1): 'FAN_MODE_MANUAL_LINEAR'}
@c.record
class SwI2cCmd_t(c.Struct):
  SIZE = 2
  ReadWriteData: int
  CmdConfig: int
SwI2cCmd_t.register_fields([('ReadWriteData', uint8_t, 0), ('CmdConfig', uint8_t, 1)])
@c.record
class SwI2cRequest_t(c.Struct):
  SIZE = 52
  I2CcontrollerPort: int
  I2CSpeed: int
  SlaveAddress: int
  NumCmds: int
  SwI2cCmds: c.Array[SwI2cCmd_t, Literal[24]]
SwI2cRequest_t.register_fields([('I2CcontrollerPort', uint8_t, 0), ('I2CSpeed', uint8_t, 1), ('SlaveAddress', uint8_t, 2), ('NumCmds', uint8_t, 3), ('SwI2cCmds', c.Array[SwI2cCmd_t, Literal[24]], 4)])
@c.record
class SwI2cRequestExternal_t(c.Struct):
  SIZE = 116
  SwI2cRequest: SwI2cRequest_t
  Spare: c.Array[ctypes.c_uint32, Literal[8]]
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
SwI2cRequestExternal_t.register_fields([('SwI2cRequest', SwI2cRequest_t, 0), ('Spare', c.Array[uint32_t, Literal[8]], 52), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 84)])
D3HOTSequence_e: dict[int, str] = {(BACO_SEQUENCE:=0): 'BACO_SEQUENCE', (MSR_SEQUENCE:=1): 'MSR_SEQUENCE', (BAMACO_SEQUENCE:=2): 'BAMACO_SEQUENCE', (ULPS_SEQUENCE:=3): 'ULPS_SEQUENCE', (D3HOT_SEQUENCE_COUNT:=4): 'D3HOT_SEQUENCE_COUNT'}
PowerGatingMode_e: dict[int, str] = {(PG_DYNAMIC_MODE:=0): 'PG_DYNAMIC_MODE', (PG_STATIC_MODE:=1): 'PG_STATIC_MODE'}
PowerGatingSettings_e: dict[int, str] = {(PG_POWER_DOWN:=0): 'PG_POWER_DOWN', (PG_POWER_UP:=1): 'PG_POWER_UP'}
@c.record
class QuadraticInt_t(c.Struct):
  SIZE = 12
  a: int
  b: int
  c: int
QuadraticInt_t.register_fields([('a', uint32_t, 0), ('b', uint32_t, 4), ('c', uint32_t, 8)])
@c.record
class QuadraticFixedPoint_t(c.Struct):
  SIZE = 12
  a: int
  b: int
  c: int
QuadraticFixedPoint_t.register_fields([('a', uint32_t, 0), ('b', uint32_t, 4), ('c', uint32_t, 8)])
@c.record
class LinearInt_t(c.Struct):
  SIZE = 8
  m: int
  b: int
LinearInt_t.register_fields([('m', uint32_t, 0), ('b', uint32_t, 4)])
@c.record
class DroopInt_t(c.Struct):
  SIZE = 12
  a: int
  b: int
  c: int
DroopInt_t.register_fields([('a', uint32_t, 0), ('b', uint32_t, 4), ('c', uint32_t, 8)])
DfllDroopModelSelect_e: dict[int, str] = {(PIECEWISE_LINEAR_FUSED_MODEL:=0): 'PIECEWISE_LINEAR_FUSED_MODEL', (PIECEWISE_LINEAR_PP_MODEL:=1): 'PIECEWISE_LINEAR_PP_MODEL', (QUADRATIC_PP_MODEL:=2): 'QUADRATIC_PP_MODEL', (PERPART_PIECEWISE_LINEAR_PP_MODEL:=3): 'PERPART_PIECEWISE_LINEAR_PP_MODEL'}
@c.record
class PiecewiseLinearDroopInt_t(c.Struct):
  SIZE = 40
  Fset: c.Array[ctypes.c_uint32, Literal[5]]
  Vdroop: c.Array[ctypes.c_uint32, Literal[5]]
PiecewiseLinearDroopInt_t.register_fields([('Fset', c.Array[uint32_t, Literal[5]], 0), ('Vdroop', c.Array[uint32_t, Literal[5]], 20)])
GFXCLK_SOURCE_e: dict[int, str] = {(GFXCLK_SOURCE_PLL:=0): 'GFXCLK_SOURCE_PLL', (GFXCLK_SOURCE_DFLL:=1): 'GFXCLK_SOURCE_DFLL', (GFXCLK_SOURCE_COUNT:=2): 'GFXCLK_SOURCE_COUNT'}
PPCLK_e: dict[int, str] = {(PPCLK_GFXCLK:=0): 'PPCLK_GFXCLK', (PPCLK_SOCCLK:=1): 'PPCLK_SOCCLK', (PPCLK_UCLK:=2): 'PPCLK_UCLK', (PPCLK_FCLK:=3): 'PPCLK_FCLK', (PPCLK_DCLK_0:=4): 'PPCLK_DCLK_0', (PPCLK_VCLK_0:=5): 'PPCLK_VCLK_0', (PPCLK_DCLK_1:=6): 'PPCLK_DCLK_1', (PPCLK_VCLK_1:=7): 'PPCLK_VCLK_1', (PPCLK_DCEFCLK:=8): 'PPCLK_DCEFCLK', (PPCLK_DISPCLK:=9): 'PPCLK_DISPCLK', (PPCLK_PIXCLK:=10): 'PPCLK_PIXCLK', (PPCLK_PHYCLK:=11): 'PPCLK_PHYCLK', (PPCLK_DTBCLK:=12): 'PPCLK_DTBCLK', (PPCLK_COUNT:=13): 'PPCLK_COUNT'}
VOLTAGE_MODE_e: dict[int, str] = {(VOLTAGE_MODE_AVFS:=0): 'VOLTAGE_MODE_AVFS', (VOLTAGE_MODE_AVFS_SS:=1): 'VOLTAGE_MODE_AVFS_SS', (VOLTAGE_MODE_SS:=2): 'VOLTAGE_MODE_SS', (VOLTAGE_MODE_COUNT:=3): 'VOLTAGE_MODE_COUNT'}
AVFS_VOLTAGE_TYPE_e: dict[int, str] = {(AVFS_VOLTAGE_GFX:=0): 'AVFS_VOLTAGE_GFX', (AVFS_VOLTAGE_SOC:=1): 'AVFS_VOLTAGE_SOC', (AVFS_VOLTAGE_COUNT:=2): 'AVFS_VOLTAGE_COUNT'}
UCLK_DIV_e: dict[int, str] = {(UCLK_DIV_BY_1:=0): 'UCLK_DIV_BY_1', (UCLK_DIV_BY_2:=1): 'UCLK_DIV_BY_2', (UCLK_DIV_BY_4:=2): 'UCLK_DIV_BY_4', (UCLK_DIV_BY_8:=3): 'UCLK_DIV_BY_8'}
GpioIntPolarity_e: dict[int, str] = {(GPIO_INT_POLARITY_ACTIVE_LOW:=0): 'GPIO_INT_POLARITY_ACTIVE_LOW', (GPIO_INT_POLARITY_ACTIVE_HIGH:=1): 'GPIO_INT_POLARITY_ACTIVE_HIGH'}
PwrConfig_e: dict[int, str] = {(PWR_CONFIG_TDP:=0): 'PWR_CONFIG_TDP', (PWR_CONFIG_TGP:=1): 'PWR_CONFIG_TGP', (PWR_CONFIG_TCP_ESTIMATED:=2): 'PWR_CONFIG_TCP_ESTIMATED', (PWR_CONFIG_TCP_MEASURED:=3): 'PWR_CONFIG_TCP_MEASURED'}
XGMI_LINK_RATE_e: dict[int, str] = {(XGMI_LINK_RATE_2:=2): 'XGMI_LINK_RATE_2', (XGMI_LINK_RATE_4:=4): 'XGMI_LINK_RATE_4', (XGMI_LINK_RATE_8:=8): 'XGMI_LINK_RATE_8', (XGMI_LINK_RATE_12:=12): 'XGMI_LINK_RATE_12', (XGMI_LINK_RATE_16:=16): 'XGMI_LINK_RATE_16', (XGMI_LINK_RATE_17:=17): 'XGMI_LINK_RATE_17', (XGMI_LINK_RATE_18:=18): 'XGMI_LINK_RATE_18', (XGMI_LINK_RATE_19:=19): 'XGMI_LINK_RATE_19', (XGMI_LINK_RATE_20:=20): 'XGMI_LINK_RATE_20', (XGMI_LINK_RATE_21:=21): 'XGMI_LINK_RATE_21', (XGMI_LINK_RATE_22:=22): 'XGMI_LINK_RATE_22', (XGMI_LINK_RATE_23:=23): 'XGMI_LINK_RATE_23', (XGMI_LINK_RATE_24:=24): 'XGMI_LINK_RATE_24', (XGMI_LINK_RATE_25:=25): 'XGMI_LINK_RATE_25', (XGMI_LINK_RATE_COUNT:=26): 'XGMI_LINK_RATE_COUNT'}
XGMI_LINK_WIDTH_e: dict[int, str] = {(XGMI_LINK_WIDTH_1:=0): 'XGMI_LINK_WIDTH_1', (XGMI_LINK_WIDTH_2:=1): 'XGMI_LINK_WIDTH_2', (XGMI_LINK_WIDTH_4:=2): 'XGMI_LINK_WIDTH_4', (XGMI_LINK_WIDTH_8:=3): 'XGMI_LINK_WIDTH_8', (XGMI_LINK_WIDTH_9:=4): 'XGMI_LINK_WIDTH_9', (XGMI_LINK_WIDTH_16:=5): 'XGMI_LINK_WIDTH_16', (XGMI_LINK_WIDTH_COUNT:=6): 'XGMI_LINK_WIDTH_COUNT'}
@c.record
class DpmDescriptor_t(c.Struct):
  SIZE = 28
  VoltageMode: int
  SnapToDiscrete: int
  NumDiscreteLevels: int
  Padding: int
  ConversionToAvfsClk: LinearInt_t
  SsCurve: QuadraticInt_t
  SsFmin: int
  Padding16: int
DpmDescriptor_t.register_fields([('VoltageMode', uint8_t, 0), ('SnapToDiscrete', uint8_t, 1), ('NumDiscreteLevels', uint8_t, 2), ('Padding', uint8_t, 3), ('ConversionToAvfsClk', LinearInt_t, 4), ('SsCurve', QuadraticInt_t, 12), ('SsFmin', uint16_t, 24), ('Padding16', uint16_t, 26)])
PPT_THROTTLER_e: dict[int, str] = {(PPT_THROTTLER_PPT0:=0): 'PPT_THROTTLER_PPT0', (PPT_THROTTLER_PPT1:=1): 'PPT_THROTTLER_PPT1', (PPT_THROTTLER_PPT2:=2): 'PPT_THROTTLER_PPT2', (PPT_THROTTLER_PPT3:=3): 'PPT_THROTTLER_PPT3', (PPT_THROTTLER_COUNT:=4): 'PPT_THROTTLER_COUNT'}
TEMP_e: dict[int, str] = {(TEMP_EDGE:=0): 'TEMP_EDGE', (TEMP_HOTSPOT:=1): 'TEMP_HOTSPOT', (TEMP_MEM:=2): 'TEMP_MEM', (TEMP_VR_GFX:=3): 'TEMP_VR_GFX', (TEMP_VR_MEM0:=4): 'TEMP_VR_MEM0', (TEMP_VR_MEM1:=5): 'TEMP_VR_MEM1', (TEMP_VR_SOC:=6): 'TEMP_VR_SOC', (TEMP_LIQUID0:=7): 'TEMP_LIQUID0', (TEMP_LIQUID1:=8): 'TEMP_LIQUID1', (TEMP_PLX:=9): 'TEMP_PLX', (TEMP_COUNT:=10): 'TEMP_COUNT'}
TDC_THROTTLER_e: dict[int, str] = {(TDC_THROTTLER_GFX:=0): 'TDC_THROTTLER_GFX', (TDC_THROTTLER_SOC:=1): 'TDC_THROTTLER_SOC', (TDC_THROTTLER_COUNT:=2): 'TDC_THROTTLER_COUNT'}
CUSTOMER_VARIANT_e: dict[int, str] = {(CUSTOMER_VARIANT_ROW:=0): 'CUSTOMER_VARIANT_ROW', (CUSTOMER_VARIANT_FALCON:=1): 'CUSTOMER_VARIANT_FALCON', (CUSTOMER_VARIANT_COUNT:=2): 'CUSTOMER_VARIANT_COUNT'}
@c.record
class UclkDpmChangeRange_t(c.Struct):
  SIZE = 4
  Fmin: int
  Fmax: int
UclkDpmChangeRange_t.register_fields([('Fmin', uint16_t, 0), ('Fmax', uint16_t, 2)])
@c.record
class PPTable_t(c.Struct):
  SIZE = 1668
  Version: int
  FeaturesToRun: c.Array[ctypes.c_uint32, Literal[2]]
  SocketPowerLimitAc: c.Array[ctypes.c_uint16, Literal[4]]
  SocketPowerLimitAcTau: c.Array[ctypes.c_uint16, Literal[4]]
  SocketPowerLimitDc: c.Array[ctypes.c_uint16, Literal[4]]
  SocketPowerLimitDcTau: c.Array[ctypes.c_uint16, Literal[4]]
  TdcLimit: c.Array[ctypes.c_uint16, Literal[2]]
  TdcLimitTau: c.Array[ctypes.c_uint16, Literal[2]]
  TemperatureLimit: c.Array[ctypes.c_uint16, Literal[10]]
  FitLimit: int
  TotalPowerConfig: int
  TotalPowerPadding: c.Array[ctypes.c_ubyte, Literal[3]]
  ApccPlusResidencyLimit: int
  SmnclkDpmFreq: c.Array[ctypes.c_uint16, Literal[2]]
  SmnclkDpmVoltage: c.Array[ctypes.c_uint16, Literal[2]]
  PaddingAPCC: int
  PerPartDroopVsetGfxDfll: c.Array[ctypes.c_uint16, Literal[5]]
  PaddingPerPartDroop: int
  ThrottlerControlMask: int
  FwDStateMask: int
  UlvVoltageOffsetSoc: int
  UlvVoltageOffsetGfx: int
  MinVoltageUlvGfx: int
  MinVoltageUlvSoc: int
  SocLIVmin: int
  PaddingLIVmin: int
  GceaLinkMgrIdleThreshold: int
  paddingRlcUlvParams: c.Array[ctypes.c_ubyte, Literal[3]]
  MinVoltageGfx: int
  MinVoltageSoc: int
  MaxVoltageGfx: int
  MaxVoltageSoc: int
  LoadLineResistanceGfx: int
  LoadLineResistanceSoc: int
  VDDGFX_TVmin: int
  VDDSOC_TVmin: int
  VDDGFX_Vmin_HiTemp: int
  VDDGFX_Vmin_LoTemp: int
  VDDSOC_Vmin_HiTemp: int
  VDDSOC_Vmin_LoTemp: int
  VDDGFX_TVminHystersis: int
  VDDSOC_TVminHystersis: int
  DpmDescriptor: c.Array[DpmDescriptor_t, Literal[13]]
  FreqTableGfx: c.Array[ctypes.c_uint16, Literal[16]]
  FreqTableVclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableDclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableSocclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableUclk: c.Array[ctypes.c_uint16, Literal[4]]
  FreqTableDcefclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableDispclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTablePixclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTablePhyclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableDtbclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableFclk: c.Array[ctypes.c_uint16, Literal[8]]
  Paddingclks: int
  PerPartDroopModelGfxDfll: c.Array[DroopInt_t, Literal[5]]
  DcModeMaxFreq: c.Array[ctypes.c_uint32, Literal[13]]
  FreqTableUclkDiv: c.Array[ctypes.c_ubyte, Literal[4]]
  FclkBoostFreq: int
  FclkParamPadding: int
  Mp0clkFreq: c.Array[ctypes.c_uint16, Literal[2]]
  Mp0DpmVoltage: c.Array[ctypes.c_uint16, Literal[2]]
  MemVddciVoltage: c.Array[ctypes.c_uint16, Literal[4]]
  MemMvddVoltage: c.Array[ctypes.c_uint16, Literal[4]]
  GfxclkFgfxoffEntry: int
  GfxclkFinit: int
  GfxclkFidle: int
  GfxclkSource: int
  GfxclkPadding: int
  GfxGpoSubFeatureMask: int
  GfxGpoEnabledWorkPolicyMask: int
  GfxGpoDisabledWorkPolicyMask: int
  GfxGpoPadding: c.Array[ctypes.c_ubyte, Literal[1]]
  GfxGpoVotingAllow: int
  GfxGpoPadding32: c.Array[ctypes.c_uint32, Literal[4]]
  GfxDcsFopt: int
  GfxDcsFclkFopt: int
  GfxDcsUclkFopt: int
  DcsGfxOffVoltage: int
  DcsMinGfxOffTime: int
  DcsMaxGfxOffTime: int
  DcsMinCreditAccum: int
  DcsExitHysteresis: int
  DcsTimeout: int
  DcsParamPadding: c.Array[ctypes.c_uint32, Literal[5]]
  FlopsPerByteTable: c.Array[ctypes.c_uint16, Literal[16]]
  LowestUclkReservedForUlv: int
  PaddingMem: c.Array[ctypes.c_ubyte, Literal[3]]
  UclkDpmPstates: c.Array[ctypes.c_ubyte, Literal[4]]
  UclkDpmSrcFreqRange: UclkDpmChangeRange_t
  UclkDpmTargFreqRange: UclkDpmChangeRange_t
  UclkDpmMidstepFreq: int
  UclkMidstepPadding: int
  PcieGenSpeed: c.Array[ctypes.c_ubyte, Literal[2]]
  PcieLaneCount: c.Array[ctypes.c_ubyte, Literal[2]]
  LclkFreq: c.Array[ctypes.c_uint16, Literal[2]]
  FanStopTemp: int
  FanStartTemp: int
  FanGain: c.Array[ctypes.c_uint16, Literal[10]]
  FanPwmMin: int
  FanAcousticLimitRpm: int
  FanThrottlingRpm: int
  FanMaximumRpm: int
  MGpuFanBoostLimitRpm: int
  FanTargetTemperature: int
  FanTargetGfxclk: int
  FanPadding16: int
  FanTempInputSelect: int
  FanPadding: int
  FanZeroRpmEnable: int
  FanTachEdgePerRev: int
  FuzzyFan_ErrorSetDelta: int
  FuzzyFan_ErrorRateSetDelta: int
  FuzzyFan_PwmSetDelta: int
  FuzzyFan_Reserved: int
  OverrideAvfsGb: c.Array[ctypes.c_ubyte, Literal[2]]
  dBtcGbGfxDfllModelSelect: int
  Padding8_Avfs: int
  qAvfsGb: c.Array[QuadraticInt_t, Literal[2]]
  dBtcGbGfxPll: DroopInt_t
  dBtcGbGfxDfll: DroopInt_t
  dBtcGbSoc: DroopInt_t
  qAgingGb: c.Array[LinearInt_t, Literal[2]]
  PiecewiseLinearDroopIntGfxDfll: PiecewiseLinearDroopInt_t
  qStaticVoltageOffset: c.Array[QuadraticInt_t, Literal[2]]
  DcTol: c.Array[ctypes.c_uint16, Literal[2]]
  DcBtcEnabled: c.Array[ctypes.c_ubyte, Literal[2]]
  Padding8_GfxBtc: c.Array[ctypes.c_ubyte, Literal[2]]
  DcBtcMin: c.Array[ctypes.c_uint16, Literal[2]]
  DcBtcMax: c.Array[ctypes.c_uint16, Literal[2]]
  DcBtcGb: c.Array[ctypes.c_uint16, Literal[2]]
  XgmiDpmPstates: c.Array[ctypes.c_ubyte, Literal[2]]
  XgmiDpmSpare: c.Array[ctypes.c_ubyte, Literal[2]]
  DebugOverrides: int
  ReservedEquation0: QuadraticInt_t
  ReservedEquation1: QuadraticInt_t
  ReservedEquation2: QuadraticInt_t
  ReservedEquation3: QuadraticInt_t
  CustomerVariant: int
  VcBtcEnabled: int
  VcBtcVminT0: int
  VcBtcFixedVminAgingOffset: int
  VcBtcVmin2PsmDegrationGb: int
  VcBtcPsmA: int
  VcBtcPsmB: int
  VcBtcVminA: int
  VcBtcVminB: int
  LedGpio: int
  GfxPowerStagesGpio: int
  SkuReserved: c.Array[ctypes.c_uint32, Literal[8]]
  GamingClk: c.Array[ctypes.c_uint32, Literal[6]]
  I2cControllers: c.Array[I2cControllerConfig_t, Literal[16]]
  GpioScl: int
  GpioSda: int
  FchUsbPdSlaveAddr: int
  I2cSpare: c.Array[ctypes.c_ubyte, Literal[1]]
  VddGfxVrMapping: int
  VddSocVrMapping: int
  VddMem0VrMapping: int
  VddMem1VrMapping: int
  GfxUlvPhaseSheddingMask: int
  SocUlvPhaseSheddingMask: int
  VddciUlvPhaseSheddingMask: int
  MvddUlvPhaseSheddingMask: int
  GfxMaxCurrent: int
  GfxOffset: int
  Padding_TelemetryGfx: int
  SocMaxCurrent: int
  SocOffset: int
  Padding_TelemetrySoc: int
  Mem0MaxCurrent: int
  Mem0Offset: int
  Padding_TelemetryMem0: int
  Mem1MaxCurrent: int
  Mem1Offset: int
  Padding_TelemetryMem1: int
  MvddRatio: int
  AcDcGpio: int
  AcDcPolarity: int
  VR0HotGpio: int
  VR0HotPolarity: int
  VR1HotGpio: int
  VR1HotPolarity: int
  GthrGpio: int
  GthrPolarity: int
  LedPin0: int
  LedPin1: int
  LedPin2: int
  LedEnableMask: int
  LedPcie: int
  LedError: int
  LedSpare1: c.Array[ctypes.c_ubyte, Literal[2]]
  PllGfxclkSpreadEnabled: int
  PllGfxclkSpreadPercent: int
  PllGfxclkSpreadFreq: int
  DfllGfxclkSpreadEnabled: int
  DfllGfxclkSpreadPercent: int
  DfllGfxclkSpreadFreq: int
  UclkSpreadPadding: int
  UclkSpreadFreq: int
  FclkSpreadEnabled: int
  FclkSpreadPercent: int
  FclkSpreadFreq: int
  MemoryChannelEnabled: int
  DramBitWidth: int
  PaddingMem1: c.Array[ctypes.c_ubyte, Literal[3]]
  TotalBoardPower: int
  BoardPowerPadding: int
  XgmiLinkSpeed: c.Array[ctypes.c_ubyte, Literal[4]]
  XgmiLinkWidth: c.Array[ctypes.c_ubyte, Literal[4]]
  XgmiFclkFreq: c.Array[ctypes.c_uint16, Literal[4]]
  XgmiSocVoltage: c.Array[ctypes.c_uint16, Literal[4]]
  HsrEnabled: int
  VddqOffEnabled: int
  PaddingUmcFlags: c.Array[ctypes.c_ubyte, Literal[2]]
  UclkSpreadPercent: c.Array[ctypes.c_ubyte, Literal[16]]
  BoardReserved: c.Array[ctypes.c_uint32, Literal[11]]
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
int16_t: TypeAlias = ctypes.c_int16
int8_t: TypeAlias = ctypes.c_byte
PPTable_t.register_fields([('Version', uint32_t, 0), ('FeaturesToRun', c.Array[uint32_t, Literal[2]], 4), ('SocketPowerLimitAc', c.Array[uint16_t, Literal[4]], 12), ('SocketPowerLimitAcTau', c.Array[uint16_t, Literal[4]], 20), ('SocketPowerLimitDc', c.Array[uint16_t, Literal[4]], 28), ('SocketPowerLimitDcTau', c.Array[uint16_t, Literal[4]], 36), ('TdcLimit', c.Array[uint16_t, Literal[2]], 44), ('TdcLimitTau', c.Array[uint16_t, Literal[2]], 48), ('TemperatureLimit', c.Array[uint16_t, Literal[10]], 52), ('FitLimit', uint32_t, 72), ('TotalPowerConfig', uint8_t, 76), ('TotalPowerPadding', c.Array[uint8_t, Literal[3]], 77), ('ApccPlusResidencyLimit', uint32_t, 80), ('SmnclkDpmFreq', c.Array[uint16_t, Literal[2]], 84), ('SmnclkDpmVoltage', c.Array[uint16_t, Literal[2]], 88), ('PaddingAPCC', uint32_t, 92), ('PerPartDroopVsetGfxDfll', c.Array[uint16_t, Literal[5]], 96), ('PaddingPerPartDroop', uint16_t, 106), ('ThrottlerControlMask', uint32_t, 108), ('FwDStateMask', uint32_t, 112), ('UlvVoltageOffsetSoc', uint16_t, 116), ('UlvVoltageOffsetGfx', uint16_t, 118), ('MinVoltageUlvGfx', uint16_t, 120), ('MinVoltageUlvSoc', uint16_t, 122), ('SocLIVmin', uint16_t, 124), ('PaddingLIVmin', uint16_t, 126), ('GceaLinkMgrIdleThreshold', uint8_t, 128), ('paddingRlcUlvParams', c.Array[uint8_t, Literal[3]], 129), ('MinVoltageGfx', uint16_t, 132), ('MinVoltageSoc', uint16_t, 134), ('MaxVoltageGfx', uint16_t, 136), ('MaxVoltageSoc', uint16_t, 138), ('LoadLineResistanceGfx', uint16_t, 140), ('LoadLineResistanceSoc', uint16_t, 142), ('VDDGFX_TVmin', uint16_t, 144), ('VDDSOC_TVmin', uint16_t, 146), ('VDDGFX_Vmin_HiTemp', uint16_t, 148), ('VDDGFX_Vmin_LoTemp', uint16_t, 150), ('VDDSOC_Vmin_HiTemp', uint16_t, 152), ('VDDSOC_Vmin_LoTemp', uint16_t, 154), ('VDDGFX_TVminHystersis', uint16_t, 156), ('VDDSOC_TVminHystersis', uint16_t, 158), ('DpmDescriptor', c.Array[DpmDescriptor_t, Literal[13]], 160), ('FreqTableGfx', c.Array[uint16_t, Literal[16]], 524), ('FreqTableVclk', c.Array[uint16_t, Literal[8]], 556), ('FreqTableDclk', c.Array[uint16_t, Literal[8]], 572), ('FreqTableSocclk', c.Array[uint16_t, Literal[8]], 588), ('FreqTableUclk', c.Array[uint16_t, Literal[4]], 604), ('FreqTableDcefclk', c.Array[uint16_t, Literal[8]], 612), ('FreqTableDispclk', c.Array[uint16_t, Literal[8]], 628), ('FreqTablePixclk', c.Array[uint16_t, Literal[8]], 644), ('FreqTablePhyclk', c.Array[uint16_t, Literal[8]], 660), ('FreqTableDtbclk', c.Array[uint16_t, Literal[8]], 676), ('FreqTableFclk', c.Array[uint16_t, Literal[8]], 692), ('Paddingclks', uint32_t, 708), ('PerPartDroopModelGfxDfll', c.Array[DroopInt_t, Literal[5]], 712), ('DcModeMaxFreq', c.Array[uint32_t, Literal[13]], 772), ('FreqTableUclkDiv', c.Array[uint8_t, Literal[4]], 824), ('FclkBoostFreq', uint16_t, 828), ('FclkParamPadding', uint16_t, 830), ('Mp0clkFreq', c.Array[uint16_t, Literal[2]], 832), ('Mp0DpmVoltage', c.Array[uint16_t, Literal[2]], 836), ('MemVddciVoltage', c.Array[uint16_t, Literal[4]], 840), ('MemMvddVoltage', c.Array[uint16_t, Literal[4]], 848), ('GfxclkFgfxoffEntry', uint16_t, 856), ('GfxclkFinit', uint16_t, 858), ('GfxclkFidle', uint16_t, 860), ('GfxclkSource', uint8_t, 862), ('GfxclkPadding', uint8_t, 863), ('GfxGpoSubFeatureMask', uint8_t, 864), ('GfxGpoEnabledWorkPolicyMask', uint8_t, 865), ('GfxGpoDisabledWorkPolicyMask', uint8_t, 866), ('GfxGpoPadding', c.Array[uint8_t, Literal[1]], 867), ('GfxGpoVotingAllow', uint32_t, 868), ('GfxGpoPadding32', c.Array[uint32_t, Literal[4]], 872), ('GfxDcsFopt', uint16_t, 888), ('GfxDcsFclkFopt', uint16_t, 890), ('GfxDcsUclkFopt', uint16_t, 892), ('DcsGfxOffVoltage', uint16_t, 894), ('DcsMinGfxOffTime', uint16_t, 896), ('DcsMaxGfxOffTime', uint16_t, 898), ('DcsMinCreditAccum', uint32_t, 900), ('DcsExitHysteresis', uint16_t, 904), ('DcsTimeout', uint16_t, 906), ('DcsParamPadding', c.Array[uint32_t, Literal[5]], 908), ('FlopsPerByteTable', c.Array[uint16_t, Literal[16]], 928), ('LowestUclkReservedForUlv', uint8_t, 960), ('PaddingMem', c.Array[uint8_t, Literal[3]], 961), ('UclkDpmPstates', c.Array[uint8_t, Literal[4]], 964), ('UclkDpmSrcFreqRange', UclkDpmChangeRange_t, 968), ('UclkDpmTargFreqRange', UclkDpmChangeRange_t, 972), ('UclkDpmMidstepFreq', uint16_t, 976), ('UclkMidstepPadding', uint16_t, 978), ('PcieGenSpeed', c.Array[uint8_t, Literal[2]], 980), ('PcieLaneCount', c.Array[uint8_t, Literal[2]], 982), ('LclkFreq', c.Array[uint16_t, Literal[2]], 984), ('FanStopTemp', uint16_t, 988), ('FanStartTemp', uint16_t, 990), ('FanGain', c.Array[uint16_t, Literal[10]], 992), ('FanPwmMin', uint16_t, 1012), ('FanAcousticLimitRpm', uint16_t, 1014), ('FanThrottlingRpm', uint16_t, 1016), ('FanMaximumRpm', uint16_t, 1018), ('MGpuFanBoostLimitRpm', uint16_t, 1020), ('FanTargetTemperature', uint16_t, 1022), ('FanTargetGfxclk', uint16_t, 1024), ('FanPadding16', uint16_t, 1026), ('FanTempInputSelect', uint8_t, 1028), ('FanPadding', uint8_t, 1029), ('FanZeroRpmEnable', uint8_t, 1030), ('FanTachEdgePerRev', uint8_t, 1031), ('FuzzyFan_ErrorSetDelta', int16_t, 1032), ('FuzzyFan_ErrorRateSetDelta', int16_t, 1034), ('FuzzyFan_PwmSetDelta', int16_t, 1036), ('FuzzyFan_Reserved', uint16_t, 1038), ('OverrideAvfsGb', c.Array[uint8_t, Literal[2]], 1040), ('dBtcGbGfxDfllModelSelect', uint8_t, 1042), ('Padding8_Avfs', uint8_t, 1043), ('qAvfsGb', c.Array[QuadraticInt_t, Literal[2]], 1044), ('dBtcGbGfxPll', DroopInt_t, 1068), ('dBtcGbGfxDfll', DroopInt_t, 1080), ('dBtcGbSoc', DroopInt_t, 1092), ('qAgingGb', c.Array[LinearInt_t, Literal[2]], 1104), ('PiecewiseLinearDroopIntGfxDfll', PiecewiseLinearDroopInt_t, 1120), ('qStaticVoltageOffset', c.Array[QuadraticInt_t, Literal[2]], 1160), ('DcTol', c.Array[uint16_t, Literal[2]], 1184), ('DcBtcEnabled', c.Array[uint8_t, Literal[2]], 1188), ('Padding8_GfxBtc', c.Array[uint8_t, Literal[2]], 1190), ('DcBtcMin', c.Array[uint16_t, Literal[2]], 1192), ('DcBtcMax', c.Array[uint16_t, Literal[2]], 1196), ('DcBtcGb', c.Array[uint16_t, Literal[2]], 1200), ('XgmiDpmPstates', c.Array[uint8_t, Literal[2]], 1204), ('XgmiDpmSpare', c.Array[uint8_t, Literal[2]], 1206), ('DebugOverrides', uint32_t, 1208), ('ReservedEquation0', QuadraticInt_t, 1212), ('ReservedEquation1', QuadraticInt_t, 1224), ('ReservedEquation2', QuadraticInt_t, 1236), ('ReservedEquation3', QuadraticInt_t, 1248), ('CustomerVariant', uint8_t, 1260), ('VcBtcEnabled', uint8_t, 1261), ('VcBtcVminT0', uint16_t, 1262), ('VcBtcFixedVminAgingOffset', uint16_t, 1264), ('VcBtcVmin2PsmDegrationGb', uint16_t, 1266), ('VcBtcPsmA', uint32_t, 1268), ('VcBtcPsmB', uint32_t, 1272), ('VcBtcVminA', uint32_t, 1276), ('VcBtcVminB', uint32_t, 1280), ('LedGpio', uint16_t, 1284), ('GfxPowerStagesGpio', uint16_t, 1286), ('SkuReserved', c.Array[uint32_t, Literal[8]], 1288), ('GamingClk', c.Array[uint32_t, Literal[6]], 1320), ('I2cControllers', c.Array[I2cControllerConfig_t, Literal[16]], 1344), ('GpioScl', uint8_t, 1472), ('GpioSda', uint8_t, 1473), ('FchUsbPdSlaveAddr', uint8_t, 1474), ('I2cSpare', c.Array[uint8_t, Literal[1]], 1475), ('VddGfxVrMapping', uint8_t, 1476), ('VddSocVrMapping', uint8_t, 1477), ('VddMem0VrMapping', uint8_t, 1478), ('VddMem1VrMapping', uint8_t, 1479), ('GfxUlvPhaseSheddingMask', uint8_t, 1480), ('SocUlvPhaseSheddingMask', uint8_t, 1481), ('VddciUlvPhaseSheddingMask', uint8_t, 1482), ('MvddUlvPhaseSheddingMask', uint8_t, 1483), ('GfxMaxCurrent', uint16_t, 1484), ('GfxOffset', int8_t, 1486), ('Padding_TelemetryGfx', uint8_t, 1487), ('SocMaxCurrent', uint16_t, 1488), ('SocOffset', int8_t, 1490), ('Padding_TelemetrySoc', uint8_t, 1491), ('Mem0MaxCurrent', uint16_t, 1492), ('Mem0Offset', int8_t, 1494), ('Padding_TelemetryMem0', uint8_t, 1495), ('Mem1MaxCurrent', uint16_t, 1496), ('Mem1Offset', int8_t, 1498), ('Padding_TelemetryMem1', uint8_t, 1499), ('MvddRatio', uint32_t, 1500), ('AcDcGpio', uint8_t, 1504), ('AcDcPolarity', uint8_t, 1505), ('VR0HotGpio', uint8_t, 1506), ('VR0HotPolarity', uint8_t, 1507), ('VR1HotGpio', uint8_t, 1508), ('VR1HotPolarity', uint8_t, 1509), ('GthrGpio', uint8_t, 1510), ('GthrPolarity', uint8_t, 1511), ('LedPin0', uint8_t, 1512), ('LedPin1', uint8_t, 1513), ('LedPin2', uint8_t, 1514), ('LedEnableMask', uint8_t, 1515), ('LedPcie', uint8_t, 1516), ('LedError', uint8_t, 1517), ('LedSpare1', c.Array[uint8_t, Literal[2]], 1518), ('PllGfxclkSpreadEnabled', uint8_t, 1520), ('PllGfxclkSpreadPercent', uint8_t, 1521), ('PllGfxclkSpreadFreq', uint16_t, 1522), ('DfllGfxclkSpreadEnabled', uint8_t, 1524), ('DfllGfxclkSpreadPercent', uint8_t, 1525), ('DfllGfxclkSpreadFreq', uint16_t, 1526), ('UclkSpreadPadding', uint16_t, 1528), ('UclkSpreadFreq', uint16_t, 1530), ('FclkSpreadEnabled', uint8_t, 1532), ('FclkSpreadPercent', uint8_t, 1533), ('FclkSpreadFreq', uint16_t, 1534), ('MemoryChannelEnabled', uint32_t, 1536), ('DramBitWidth', uint8_t, 1540), ('PaddingMem1', c.Array[uint8_t, Literal[3]], 1541), ('TotalBoardPower', uint16_t, 1544), ('BoardPowerPadding', uint16_t, 1546), ('XgmiLinkSpeed', c.Array[uint8_t, Literal[4]], 1548), ('XgmiLinkWidth', c.Array[uint8_t, Literal[4]], 1552), ('XgmiFclkFreq', c.Array[uint16_t, Literal[4]], 1556), ('XgmiSocVoltage', c.Array[uint16_t, Literal[4]], 1564), ('HsrEnabled', uint8_t, 1572), ('VddqOffEnabled', uint8_t, 1573), ('PaddingUmcFlags', c.Array[uint8_t, Literal[2]], 1574), ('UclkSpreadPercent', c.Array[uint8_t, Literal[16]], 1576), ('BoardReserved', c.Array[uint32_t, Literal[11]], 1592), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 1636)])
@c.record
class PPTable_beige_goby_t(c.Struct):
  SIZE = 1888
  Version: int
  FeaturesToRun: c.Array[ctypes.c_uint32, Literal[2]]
  SocketPowerLimitAc: c.Array[ctypes.c_uint16, Literal[4]]
  SocketPowerLimitAcTau: c.Array[ctypes.c_uint16, Literal[4]]
  SocketPowerLimitDc: c.Array[ctypes.c_uint16, Literal[4]]
  SocketPowerLimitDcTau: c.Array[ctypes.c_uint16, Literal[4]]
  TdcLimit: c.Array[ctypes.c_uint16, Literal[2]]
  TdcLimitTau: c.Array[ctypes.c_uint16, Literal[2]]
  TemperatureLimit: c.Array[ctypes.c_uint16, Literal[10]]
  FitLimit: int
  TotalPowerConfig: int
  TotalPowerPadding: c.Array[ctypes.c_ubyte, Literal[3]]
  ApccPlusResidencyLimit: int
  SmnclkDpmFreq: c.Array[ctypes.c_uint16, Literal[2]]
  SmnclkDpmVoltage: c.Array[ctypes.c_uint16, Literal[2]]
  PaddingAPCC: int
  PerPartDroopVsetGfxDfll: c.Array[ctypes.c_uint16, Literal[5]]
  PaddingPerPartDroop: int
  ThrottlerControlMask: int
  FwDStateMask: int
  UlvVoltageOffsetSoc: int
  UlvVoltageOffsetGfx: int
  MinVoltageUlvGfx: int
  MinVoltageUlvSoc: int
  SocLIVmin: int
  SocLIVminoffset: int
  GceaLinkMgrIdleThreshold: int
  paddingRlcUlvParams: c.Array[ctypes.c_ubyte, Literal[3]]
  MinVoltageGfx: int
  MinVoltageSoc: int
  MaxVoltageGfx: int
  MaxVoltageSoc: int
  LoadLineResistanceGfx: int
  LoadLineResistanceSoc: int
  VDDGFX_TVmin: int
  VDDSOC_TVmin: int
  VDDGFX_Vmin_HiTemp: int
  VDDGFX_Vmin_LoTemp: int
  VDDSOC_Vmin_HiTemp: int
  VDDSOC_Vmin_LoTemp: int
  VDDGFX_TVminHystersis: int
  VDDSOC_TVminHystersis: int
  DpmDescriptor: c.Array[DpmDescriptor_t, Literal[13]]
  FreqTableGfx: c.Array[ctypes.c_uint16, Literal[16]]
  FreqTableVclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableDclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableSocclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableUclk: c.Array[ctypes.c_uint16, Literal[4]]
  FreqTableDcefclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableDispclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTablePixclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTablePhyclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableDtbclk: c.Array[ctypes.c_uint16, Literal[8]]
  FreqTableFclk: c.Array[ctypes.c_uint16, Literal[8]]
  Paddingclks: int
  PerPartDroopModelGfxDfll: c.Array[DroopInt_t, Literal[5]]
  DcModeMaxFreq: c.Array[ctypes.c_uint32, Literal[13]]
  FreqTableUclkDiv: c.Array[ctypes.c_ubyte, Literal[4]]
  FclkBoostFreq: int
  FclkParamPadding: int
  Mp0clkFreq: c.Array[ctypes.c_uint16, Literal[2]]
  Mp0DpmVoltage: c.Array[ctypes.c_uint16, Literal[2]]
  MemVddciVoltage: c.Array[ctypes.c_uint16, Literal[4]]
  MemMvddVoltage: c.Array[ctypes.c_uint16, Literal[4]]
  GfxclkFgfxoffEntry: int
  GfxclkFinit: int
  GfxclkFidle: int
  GfxclkSource: int
  GfxclkPadding: int
  GfxGpoSubFeatureMask: int
  GfxGpoEnabledWorkPolicyMask: int
  GfxGpoDisabledWorkPolicyMask: int
  GfxGpoPadding: c.Array[ctypes.c_ubyte, Literal[1]]
  GfxGpoVotingAllow: int
  GfxGpoPadding32: c.Array[ctypes.c_uint32, Literal[4]]
  GfxDcsFopt: int
  GfxDcsFclkFopt: int
  GfxDcsUclkFopt: int
  DcsGfxOffVoltage: int
  DcsMinGfxOffTime: int
  DcsMaxGfxOffTime: int
  DcsMinCreditAccum: int
  DcsExitHysteresis: int
  DcsTimeout: int
  DcsParamPadding: c.Array[ctypes.c_uint32, Literal[5]]
  FlopsPerByteTable: c.Array[ctypes.c_uint16, Literal[16]]
  LowestUclkReservedForUlv: int
  PaddingMem: c.Array[ctypes.c_ubyte, Literal[3]]
  UclkDpmPstates: c.Array[ctypes.c_ubyte, Literal[4]]
  UclkDpmSrcFreqRange: UclkDpmChangeRange_t
  UclkDpmTargFreqRange: UclkDpmChangeRange_t
  UclkDpmMidstepFreq: int
  UclkMidstepPadding: int
  PcieGenSpeed: c.Array[ctypes.c_ubyte, Literal[2]]
  PcieLaneCount: c.Array[ctypes.c_ubyte, Literal[2]]
  LclkFreq: c.Array[ctypes.c_uint16, Literal[2]]
  FanStopTemp: int
  FanStartTemp: int
  FanGain: c.Array[ctypes.c_uint16, Literal[10]]
  FanPwmMin: int
  FanAcousticLimitRpm: int
  FanThrottlingRpm: int
  FanMaximumRpm: int
  MGpuFanBoostLimitRpm: int
  FanTargetTemperature: int
  FanTargetGfxclk: int
  FanPadding16: int
  FanTempInputSelect: int
  FanPadding: int
  FanZeroRpmEnable: int
  FanTachEdgePerRev: int
  FuzzyFan_ErrorSetDelta: int
  FuzzyFan_ErrorRateSetDelta: int
  FuzzyFan_PwmSetDelta: int
  FuzzyFan_Reserved: int
  OverrideAvfsGb: c.Array[ctypes.c_ubyte, Literal[2]]
  dBtcGbGfxDfllModelSelect: int
  Padding8_Avfs: int
  qAvfsGb: c.Array[QuadraticInt_t, Literal[2]]
  dBtcGbGfxPll: DroopInt_t
  dBtcGbGfxDfll: DroopInt_t
  dBtcGbSoc: DroopInt_t
  qAgingGb: c.Array[LinearInt_t, Literal[2]]
  PiecewiseLinearDroopIntGfxDfll: PiecewiseLinearDroopInt_t
  qStaticVoltageOffset: c.Array[QuadraticInt_t, Literal[2]]
  DcTol: c.Array[ctypes.c_uint16, Literal[2]]
  DcBtcEnabled: c.Array[ctypes.c_ubyte, Literal[2]]
  Padding8_GfxBtc: c.Array[ctypes.c_ubyte, Literal[2]]
  DcBtcMin: c.Array[ctypes.c_uint16, Literal[2]]
  DcBtcMax: c.Array[ctypes.c_uint16, Literal[2]]
  DcBtcGb: c.Array[ctypes.c_uint16, Literal[2]]
  XgmiDpmPstates: c.Array[ctypes.c_ubyte, Literal[2]]
  XgmiDpmSpare: c.Array[ctypes.c_ubyte, Literal[2]]
  DebugOverrides: int
  ReservedEquation0: QuadraticInt_t
  ReservedEquation1: QuadraticInt_t
  ReservedEquation2: QuadraticInt_t
  ReservedEquation3: QuadraticInt_t
  CustomerVariant: int
  VcBtcEnabled: int
  VcBtcVminT0: int
  VcBtcFixedVminAgingOffset: int
  VcBtcVmin2PsmDegrationGb: int
  VcBtcPsmA: int
  VcBtcPsmB: int
  VcBtcVminA: int
  VcBtcVminB: int
  LedGpio: int
  GfxPowerStagesGpio: int
  SkuReserved: c.Array[ctypes.c_uint32, Literal[63]]
  GamingClk: c.Array[ctypes.c_uint32, Literal[6]]
  I2cControllers: c.Array[I2cControllerConfig_t, Literal[16]]
  GpioScl: int
  GpioSda: int
  FchUsbPdSlaveAddr: int
  I2cSpare: c.Array[ctypes.c_ubyte, Literal[1]]
  VddGfxVrMapping: int
  VddSocVrMapping: int
  VddMem0VrMapping: int
  VddMem1VrMapping: int
  GfxUlvPhaseSheddingMask: int
  SocUlvPhaseSheddingMask: int
  VddciUlvPhaseSheddingMask: int
  MvddUlvPhaseSheddingMask: int
  GfxMaxCurrent: int
  GfxOffset: int
  Padding_TelemetryGfx: int
  SocMaxCurrent: int
  SocOffset: int
  Padding_TelemetrySoc: int
  Mem0MaxCurrent: int
  Mem0Offset: int
  Padding_TelemetryMem0: int
  Mem1MaxCurrent: int
  Mem1Offset: int
  Padding_TelemetryMem1: int
  MvddRatio: int
  AcDcGpio: int
  AcDcPolarity: int
  VR0HotGpio: int
  VR0HotPolarity: int
  VR1HotGpio: int
  VR1HotPolarity: int
  GthrGpio: int
  GthrPolarity: int
  LedPin0: int
  LedPin1: int
  LedPin2: int
  LedEnableMask: int
  LedPcie: int
  LedError: int
  LedSpare1: c.Array[ctypes.c_ubyte, Literal[2]]
  PllGfxclkSpreadEnabled: int
  PllGfxclkSpreadPercent: int
  PllGfxclkSpreadFreq: int
  DfllGfxclkSpreadEnabled: int
  DfllGfxclkSpreadPercent: int
  DfllGfxclkSpreadFreq: int
  UclkSpreadPadding: int
  UclkSpreadFreq: int
  FclkSpreadEnabled: int
  FclkSpreadPercent: int
  FclkSpreadFreq: int
  MemoryChannelEnabled: int
  DramBitWidth: int
  PaddingMem1: c.Array[ctypes.c_ubyte, Literal[3]]
  TotalBoardPower: int
  BoardPowerPadding: int
  XgmiLinkSpeed: c.Array[ctypes.c_ubyte, Literal[4]]
  XgmiLinkWidth: c.Array[ctypes.c_ubyte, Literal[4]]
  XgmiFclkFreq: c.Array[ctypes.c_uint16, Literal[4]]
  XgmiSocVoltage: c.Array[ctypes.c_uint16, Literal[4]]
  HsrEnabled: int
  VddqOffEnabled: int
  PaddingUmcFlags: c.Array[ctypes.c_ubyte, Literal[2]]
  UclkSpreadPercent: c.Array[ctypes.c_ubyte, Literal[16]]
  BoardReserved: c.Array[ctypes.c_uint32, Literal[11]]
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
PPTable_beige_goby_t.register_fields([('Version', uint32_t, 0), ('FeaturesToRun', c.Array[uint32_t, Literal[2]], 4), ('SocketPowerLimitAc', c.Array[uint16_t, Literal[4]], 12), ('SocketPowerLimitAcTau', c.Array[uint16_t, Literal[4]], 20), ('SocketPowerLimitDc', c.Array[uint16_t, Literal[4]], 28), ('SocketPowerLimitDcTau', c.Array[uint16_t, Literal[4]], 36), ('TdcLimit', c.Array[uint16_t, Literal[2]], 44), ('TdcLimitTau', c.Array[uint16_t, Literal[2]], 48), ('TemperatureLimit', c.Array[uint16_t, Literal[10]], 52), ('FitLimit', uint32_t, 72), ('TotalPowerConfig', uint8_t, 76), ('TotalPowerPadding', c.Array[uint8_t, Literal[3]], 77), ('ApccPlusResidencyLimit', uint32_t, 80), ('SmnclkDpmFreq', c.Array[uint16_t, Literal[2]], 84), ('SmnclkDpmVoltage', c.Array[uint16_t, Literal[2]], 88), ('PaddingAPCC', uint32_t, 92), ('PerPartDroopVsetGfxDfll', c.Array[uint16_t, Literal[5]], 96), ('PaddingPerPartDroop', uint16_t, 106), ('ThrottlerControlMask', uint32_t, 108), ('FwDStateMask', uint32_t, 112), ('UlvVoltageOffsetSoc', uint16_t, 116), ('UlvVoltageOffsetGfx', uint16_t, 118), ('MinVoltageUlvGfx', uint16_t, 120), ('MinVoltageUlvSoc', uint16_t, 122), ('SocLIVmin', uint16_t, 124), ('SocLIVminoffset', uint16_t, 126), ('GceaLinkMgrIdleThreshold', uint8_t, 128), ('paddingRlcUlvParams', c.Array[uint8_t, Literal[3]], 129), ('MinVoltageGfx', uint16_t, 132), ('MinVoltageSoc', uint16_t, 134), ('MaxVoltageGfx', uint16_t, 136), ('MaxVoltageSoc', uint16_t, 138), ('LoadLineResistanceGfx', uint16_t, 140), ('LoadLineResistanceSoc', uint16_t, 142), ('VDDGFX_TVmin', uint16_t, 144), ('VDDSOC_TVmin', uint16_t, 146), ('VDDGFX_Vmin_HiTemp', uint16_t, 148), ('VDDGFX_Vmin_LoTemp', uint16_t, 150), ('VDDSOC_Vmin_HiTemp', uint16_t, 152), ('VDDSOC_Vmin_LoTemp', uint16_t, 154), ('VDDGFX_TVminHystersis', uint16_t, 156), ('VDDSOC_TVminHystersis', uint16_t, 158), ('DpmDescriptor', c.Array[DpmDescriptor_t, Literal[13]], 160), ('FreqTableGfx', c.Array[uint16_t, Literal[16]], 524), ('FreqTableVclk', c.Array[uint16_t, Literal[8]], 556), ('FreqTableDclk', c.Array[uint16_t, Literal[8]], 572), ('FreqTableSocclk', c.Array[uint16_t, Literal[8]], 588), ('FreqTableUclk', c.Array[uint16_t, Literal[4]], 604), ('FreqTableDcefclk', c.Array[uint16_t, Literal[8]], 612), ('FreqTableDispclk', c.Array[uint16_t, Literal[8]], 628), ('FreqTablePixclk', c.Array[uint16_t, Literal[8]], 644), ('FreqTablePhyclk', c.Array[uint16_t, Literal[8]], 660), ('FreqTableDtbclk', c.Array[uint16_t, Literal[8]], 676), ('FreqTableFclk', c.Array[uint16_t, Literal[8]], 692), ('Paddingclks', uint32_t, 708), ('PerPartDroopModelGfxDfll', c.Array[DroopInt_t, Literal[5]], 712), ('DcModeMaxFreq', c.Array[uint32_t, Literal[13]], 772), ('FreqTableUclkDiv', c.Array[uint8_t, Literal[4]], 824), ('FclkBoostFreq', uint16_t, 828), ('FclkParamPadding', uint16_t, 830), ('Mp0clkFreq', c.Array[uint16_t, Literal[2]], 832), ('Mp0DpmVoltage', c.Array[uint16_t, Literal[2]], 836), ('MemVddciVoltage', c.Array[uint16_t, Literal[4]], 840), ('MemMvddVoltage', c.Array[uint16_t, Literal[4]], 848), ('GfxclkFgfxoffEntry', uint16_t, 856), ('GfxclkFinit', uint16_t, 858), ('GfxclkFidle', uint16_t, 860), ('GfxclkSource', uint8_t, 862), ('GfxclkPadding', uint8_t, 863), ('GfxGpoSubFeatureMask', uint8_t, 864), ('GfxGpoEnabledWorkPolicyMask', uint8_t, 865), ('GfxGpoDisabledWorkPolicyMask', uint8_t, 866), ('GfxGpoPadding', c.Array[uint8_t, Literal[1]], 867), ('GfxGpoVotingAllow', uint32_t, 868), ('GfxGpoPadding32', c.Array[uint32_t, Literal[4]], 872), ('GfxDcsFopt', uint16_t, 888), ('GfxDcsFclkFopt', uint16_t, 890), ('GfxDcsUclkFopt', uint16_t, 892), ('DcsGfxOffVoltage', uint16_t, 894), ('DcsMinGfxOffTime', uint16_t, 896), ('DcsMaxGfxOffTime', uint16_t, 898), ('DcsMinCreditAccum', uint32_t, 900), ('DcsExitHysteresis', uint16_t, 904), ('DcsTimeout', uint16_t, 906), ('DcsParamPadding', c.Array[uint32_t, Literal[5]], 908), ('FlopsPerByteTable', c.Array[uint16_t, Literal[16]], 928), ('LowestUclkReservedForUlv', uint8_t, 960), ('PaddingMem', c.Array[uint8_t, Literal[3]], 961), ('UclkDpmPstates', c.Array[uint8_t, Literal[4]], 964), ('UclkDpmSrcFreqRange', UclkDpmChangeRange_t, 968), ('UclkDpmTargFreqRange', UclkDpmChangeRange_t, 972), ('UclkDpmMidstepFreq', uint16_t, 976), ('UclkMidstepPadding', uint16_t, 978), ('PcieGenSpeed', c.Array[uint8_t, Literal[2]], 980), ('PcieLaneCount', c.Array[uint8_t, Literal[2]], 982), ('LclkFreq', c.Array[uint16_t, Literal[2]], 984), ('FanStopTemp', uint16_t, 988), ('FanStartTemp', uint16_t, 990), ('FanGain', c.Array[uint16_t, Literal[10]], 992), ('FanPwmMin', uint16_t, 1012), ('FanAcousticLimitRpm', uint16_t, 1014), ('FanThrottlingRpm', uint16_t, 1016), ('FanMaximumRpm', uint16_t, 1018), ('MGpuFanBoostLimitRpm', uint16_t, 1020), ('FanTargetTemperature', uint16_t, 1022), ('FanTargetGfxclk', uint16_t, 1024), ('FanPadding16', uint16_t, 1026), ('FanTempInputSelect', uint8_t, 1028), ('FanPadding', uint8_t, 1029), ('FanZeroRpmEnable', uint8_t, 1030), ('FanTachEdgePerRev', uint8_t, 1031), ('FuzzyFan_ErrorSetDelta', int16_t, 1032), ('FuzzyFan_ErrorRateSetDelta', int16_t, 1034), ('FuzzyFan_PwmSetDelta', int16_t, 1036), ('FuzzyFan_Reserved', uint16_t, 1038), ('OverrideAvfsGb', c.Array[uint8_t, Literal[2]], 1040), ('dBtcGbGfxDfllModelSelect', uint8_t, 1042), ('Padding8_Avfs', uint8_t, 1043), ('qAvfsGb', c.Array[QuadraticInt_t, Literal[2]], 1044), ('dBtcGbGfxPll', DroopInt_t, 1068), ('dBtcGbGfxDfll', DroopInt_t, 1080), ('dBtcGbSoc', DroopInt_t, 1092), ('qAgingGb', c.Array[LinearInt_t, Literal[2]], 1104), ('PiecewiseLinearDroopIntGfxDfll', PiecewiseLinearDroopInt_t, 1120), ('qStaticVoltageOffset', c.Array[QuadraticInt_t, Literal[2]], 1160), ('DcTol', c.Array[uint16_t, Literal[2]], 1184), ('DcBtcEnabled', c.Array[uint8_t, Literal[2]], 1188), ('Padding8_GfxBtc', c.Array[uint8_t, Literal[2]], 1190), ('DcBtcMin', c.Array[uint16_t, Literal[2]], 1192), ('DcBtcMax', c.Array[uint16_t, Literal[2]], 1196), ('DcBtcGb', c.Array[uint16_t, Literal[2]], 1200), ('XgmiDpmPstates', c.Array[uint8_t, Literal[2]], 1204), ('XgmiDpmSpare', c.Array[uint8_t, Literal[2]], 1206), ('DebugOverrides', uint32_t, 1208), ('ReservedEquation0', QuadraticInt_t, 1212), ('ReservedEquation1', QuadraticInt_t, 1224), ('ReservedEquation2', QuadraticInt_t, 1236), ('ReservedEquation3', QuadraticInt_t, 1248), ('CustomerVariant', uint8_t, 1260), ('VcBtcEnabled', uint8_t, 1261), ('VcBtcVminT0', uint16_t, 1262), ('VcBtcFixedVminAgingOffset', uint16_t, 1264), ('VcBtcVmin2PsmDegrationGb', uint16_t, 1266), ('VcBtcPsmA', uint32_t, 1268), ('VcBtcPsmB', uint32_t, 1272), ('VcBtcVminA', uint32_t, 1276), ('VcBtcVminB', uint32_t, 1280), ('LedGpio', uint16_t, 1284), ('GfxPowerStagesGpio', uint16_t, 1286), ('SkuReserved', c.Array[uint32_t, Literal[63]], 1288), ('GamingClk', c.Array[uint32_t, Literal[6]], 1540), ('I2cControllers', c.Array[I2cControllerConfig_t, Literal[16]], 1564), ('GpioScl', uint8_t, 1692), ('GpioSda', uint8_t, 1693), ('FchUsbPdSlaveAddr', uint8_t, 1694), ('I2cSpare', c.Array[uint8_t, Literal[1]], 1695), ('VddGfxVrMapping', uint8_t, 1696), ('VddSocVrMapping', uint8_t, 1697), ('VddMem0VrMapping', uint8_t, 1698), ('VddMem1VrMapping', uint8_t, 1699), ('GfxUlvPhaseSheddingMask', uint8_t, 1700), ('SocUlvPhaseSheddingMask', uint8_t, 1701), ('VddciUlvPhaseSheddingMask', uint8_t, 1702), ('MvddUlvPhaseSheddingMask', uint8_t, 1703), ('GfxMaxCurrent', uint16_t, 1704), ('GfxOffset', int8_t, 1706), ('Padding_TelemetryGfx', uint8_t, 1707), ('SocMaxCurrent', uint16_t, 1708), ('SocOffset', int8_t, 1710), ('Padding_TelemetrySoc', uint8_t, 1711), ('Mem0MaxCurrent', uint16_t, 1712), ('Mem0Offset', int8_t, 1714), ('Padding_TelemetryMem0', uint8_t, 1715), ('Mem1MaxCurrent', uint16_t, 1716), ('Mem1Offset', int8_t, 1718), ('Padding_TelemetryMem1', uint8_t, 1719), ('MvddRatio', uint32_t, 1720), ('AcDcGpio', uint8_t, 1724), ('AcDcPolarity', uint8_t, 1725), ('VR0HotGpio', uint8_t, 1726), ('VR0HotPolarity', uint8_t, 1727), ('VR1HotGpio', uint8_t, 1728), ('VR1HotPolarity', uint8_t, 1729), ('GthrGpio', uint8_t, 1730), ('GthrPolarity', uint8_t, 1731), ('LedPin0', uint8_t, 1732), ('LedPin1', uint8_t, 1733), ('LedPin2', uint8_t, 1734), ('LedEnableMask', uint8_t, 1735), ('LedPcie', uint8_t, 1736), ('LedError', uint8_t, 1737), ('LedSpare1', c.Array[uint8_t, Literal[2]], 1738), ('PllGfxclkSpreadEnabled', uint8_t, 1740), ('PllGfxclkSpreadPercent', uint8_t, 1741), ('PllGfxclkSpreadFreq', uint16_t, 1742), ('DfllGfxclkSpreadEnabled', uint8_t, 1744), ('DfllGfxclkSpreadPercent', uint8_t, 1745), ('DfllGfxclkSpreadFreq', uint16_t, 1746), ('UclkSpreadPadding', uint16_t, 1748), ('UclkSpreadFreq', uint16_t, 1750), ('FclkSpreadEnabled', uint8_t, 1752), ('FclkSpreadPercent', uint8_t, 1753), ('FclkSpreadFreq', uint16_t, 1754), ('MemoryChannelEnabled', uint32_t, 1756), ('DramBitWidth', uint8_t, 1760), ('PaddingMem1', c.Array[uint8_t, Literal[3]], 1761), ('TotalBoardPower', uint16_t, 1764), ('BoardPowerPadding', uint16_t, 1766), ('XgmiLinkSpeed', c.Array[uint8_t, Literal[4]], 1768), ('XgmiLinkWidth', c.Array[uint8_t, Literal[4]], 1772), ('XgmiFclkFreq', c.Array[uint16_t, Literal[4]], 1776), ('XgmiSocVoltage', c.Array[uint16_t, Literal[4]], 1784), ('HsrEnabled', uint8_t, 1792), ('VddqOffEnabled', uint8_t, 1793), ('PaddingUmcFlags', c.Array[uint8_t, Literal[2]], 1794), ('UclkSpreadPercent', c.Array[uint8_t, Literal[16]], 1796), ('BoardReserved', c.Array[uint32_t, Literal[11]], 1812), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 1856)])
@c.record
class DriverSmuConfig_t(c.Struct):
  SIZE = 16
  GfxclkAverageLpfTau: int
  FclkAverageLpfTau: int
  UclkAverageLpfTau: int
  GfxActivityLpfTau: int
  UclkActivityLpfTau: int
  SocketPowerLpfTau: int
  VcnClkAverageLpfTau: int
  padding16: int
DriverSmuConfig_t.register_fields([('GfxclkAverageLpfTau', uint16_t, 0), ('FclkAverageLpfTau', uint16_t, 2), ('UclkAverageLpfTau', uint16_t, 4), ('GfxActivityLpfTau', uint16_t, 6), ('UclkActivityLpfTau', uint16_t, 8), ('SocketPowerLpfTau', uint16_t, 10), ('VcnClkAverageLpfTau', uint16_t, 12), ('padding16', uint16_t, 14)])
@c.record
class DriverSmuConfigExternal_t(c.Struct):
  SIZE = 76
  DriverSmuConfig: DriverSmuConfig_t
  Spare: c.Array[ctypes.c_uint32, Literal[7]]
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
DriverSmuConfigExternal_t.register_fields([('DriverSmuConfig', DriverSmuConfig_t, 0), ('Spare', c.Array[uint32_t, Literal[7]], 16), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 44)])
@c.record
class OverDriveTable_t(c.Struct):
  SIZE = 52
  GfxclkFmin: int
  GfxclkFmax: int
  CustomGfxVfCurve: QuadraticInt_t
  CustomCurveFmin: int
  UclkFmin: int
  UclkFmax: int
  OverDrivePct: int
  FanMaximumRpm: int
  FanMinimumPwm: int
  FanAcousticLimitRpm: int
  FanTargetTemperature: int
  FanLinearPwmPoints: c.Array[ctypes.c_ubyte, Literal[6]]
  FanLinearTempPoints: c.Array[ctypes.c_ubyte, Literal[6]]
  MaxOpTemp: int
  VddGfxOffset: int
  FanZeroRpmEnable: int
  FanZeroRpmStopTemp: int
  FanMode: int
  Padding: c.Array[ctypes.c_ubyte, Literal[1]]
OverDriveTable_t.register_fields([('GfxclkFmin', uint16_t, 0), ('GfxclkFmax', uint16_t, 2), ('CustomGfxVfCurve', QuadraticInt_t, 4), ('CustomCurveFmin', uint16_t, 16), ('UclkFmin', uint16_t, 18), ('UclkFmax', uint16_t, 20), ('OverDrivePct', int16_t, 22), ('FanMaximumRpm', uint16_t, 24), ('FanMinimumPwm', uint16_t, 26), ('FanAcousticLimitRpm', uint16_t, 28), ('FanTargetTemperature', uint16_t, 30), ('FanLinearPwmPoints', c.Array[uint8_t, Literal[6]], 32), ('FanLinearTempPoints', c.Array[uint8_t, Literal[6]], 38), ('MaxOpTemp', uint16_t, 44), ('VddGfxOffset', int16_t, 46), ('FanZeroRpmEnable', uint8_t, 48), ('FanZeroRpmStopTemp', uint8_t, 49), ('FanMode', uint8_t, 50), ('Padding', c.Array[uint8_t, Literal[1]], 51)])
@c.record
class OverDriveTableExternal_t(c.Struct):
  SIZE = 116
  OverDriveTable: OverDriveTable_t
  Spare: c.Array[ctypes.c_uint32, Literal[8]]
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
OverDriveTableExternal_t.register_fields([('OverDriveTable', OverDriveTable_t, 0), ('Spare', c.Array[uint32_t, Literal[8]], 52), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 84)])
@c.record
class SmuMetrics_t(c.Struct):
  SIZE = 136
  CurrClock: c.Array[ctypes.c_uint32, Literal[13]]
  AverageGfxclkFrequencyPreDs: int
  AverageGfxclkFrequencyPostDs: int
  AverageFclkFrequencyPreDs: int
  AverageFclkFrequencyPostDs: int
  AverageUclkFrequencyPreDs: int
  AverageUclkFrequencyPostDs: int
  AverageGfxActivity: int
  AverageUclkActivity: int
  CurrSocVoltageOffset: int
  CurrGfxVoltageOffset: int
  CurrMemVidOffset: int
  Padding8: int
  AverageSocketPower: int
  TemperatureEdge: int
  TemperatureHotspot: int
  TemperatureMem: int
  TemperatureVrGfx: int
  TemperatureVrMem0: int
  TemperatureVrMem1: int
  TemperatureVrSoc: int
  TemperatureLiquid0: int
  TemperatureLiquid1: int
  TemperaturePlx: int
  Padding16: int
  ThrottlerStatus: int
  LinkDpmLevel: int
  CurrFanPwm: int
  CurrFanSpeed: int
  D3HotEntryCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  D3HotExitCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  ArmMsgReceivedCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  EnergyAccumulator: int
  AverageVclk0Frequency: int
  AverageDclk0Frequency: int
  AverageVclk1Frequency: int
  AverageDclk1Frequency: int
  VcnActivityPercentage: int
  PcieRate: int
  PcieWidth: int
  AverageGfxclkFrequencyTarget: int
  Padding16_2: int
SmuMetrics_t.register_fields([('CurrClock', c.Array[uint32_t, Literal[13]], 0), ('AverageGfxclkFrequencyPreDs', uint16_t, 52), ('AverageGfxclkFrequencyPostDs', uint16_t, 54), ('AverageFclkFrequencyPreDs', uint16_t, 56), ('AverageFclkFrequencyPostDs', uint16_t, 58), ('AverageUclkFrequencyPreDs', uint16_t, 60), ('AverageUclkFrequencyPostDs', uint16_t, 62), ('AverageGfxActivity', uint16_t, 64), ('AverageUclkActivity', uint16_t, 66), ('CurrSocVoltageOffset', uint8_t, 68), ('CurrGfxVoltageOffset', uint8_t, 69), ('CurrMemVidOffset', uint8_t, 70), ('Padding8', uint8_t, 71), ('AverageSocketPower', uint16_t, 72), ('TemperatureEdge', uint16_t, 74), ('TemperatureHotspot', uint16_t, 76), ('TemperatureMem', uint16_t, 78), ('TemperatureVrGfx', uint16_t, 80), ('TemperatureVrMem0', uint16_t, 82), ('TemperatureVrMem1', uint16_t, 84), ('TemperatureVrSoc', uint16_t, 86), ('TemperatureLiquid0', uint16_t, 88), ('TemperatureLiquid1', uint16_t, 90), ('TemperaturePlx', uint16_t, 92), ('Padding16', uint16_t, 94), ('ThrottlerStatus', uint32_t, 96), ('LinkDpmLevel', uint8_t, 100), ('CurrFanPwm', uint8_t, 101), ('CurrFanSpeed', uint16_t, 102), ('D3HotEntryCountPerMode', c.Array[uint8_t, Literal[4]], 104), ('D3HotExitCountPerMode', c.Array[uint8_t, Literal[4]], 108), ('ArmMsgReceivedCountPerMode', c.Array[uint8_t, Literal[4]], 112), ('EnergyAccumulator', uint32_t, 116), ('AverageVclk0Frequency', uint16_t, 120), ('AverageDclk0Frequency', uint16_t, 122), ('AverageVclk1Frequency', uint16_t, 124), ('AverageDclk1Frequency', uint16_t, 126), ('VcnActivityPercentage', uint16_t, 128), ('PcieRate', uint8_t, 130), ('PcieWidth', uint8_t, 131), ('AverageGfxclkFrequencyTarget', uint16_t, 132), ('Padding16_2', uint16_t, 134)])
@c.record
class SmuMetrics_V2_t(c.Struct):
  SIZE = 156
  CurrClock: c.Array[ctypes.c_uint32, Literal[13]]
  AverageGfxclkFrequencyPreDs: int
  AverageGfxclkFrequencyPostDs: int
  AverageFclkFrequencyPreDs: int
  AverageFclkFrequencyPostDs: int
  AverageUclkFrequencyPreDs: int
  AverageUclkFrequencyPostDs: int
  AverageGfxActivity: int
  AverageUclkActivity: int
  CurrSocVoltageOffset: int
  CurrGfxVoltageOffset: int
  CurrMemVidOffset: int
  Padding8: int
  AverageSocketPower: int
  TemperatureEdge: int
  TemperatureHotspot: int
  TemperatureMem: int
  TemperatureVrGfx: int
  TemperatureVrMem0: int
  TemperatureVrMem1: int
  TemperatureVrSoc: int
  TemperatureLiquid0: int
  TemperatureLiquid1: int
  TemperaturePlx: int
  Padding16: int
  AccCnt: int
  ThrottlingPercentage: c.Array[ctypes.c_ubyte, Literal[20]]
  LinkDpmLevel: int
  CurrFanPwm: int
  CurrFanSpeed: int
  D3HotEntryCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  D3HotExitCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  ArmMsgReceivedCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  EnergyAccumulator: int
  AverageVclk0Frequency: int
  AverageDclk0Frequency: int
  AverageVclk1Frequency: int
  AverageDclk1Frequency: int
  VcnActivityPercentage: int
  PcieRate: int
  PcieWidth: int
  AverageGfxclkFrequencyTarget: int
  Padding16_2: int
SmuMetrics_V2_t.register_fields([('CurrClock', c.Array[uint32_t, Literal[13]], 0), ('AverageGfxclkFrequencyPreDs', uint16_t, 52), ('AverageGfxclkFrequencyPostDs', uint16_t, 54), ('AverageFclkFrequencyPreDs', uint16_t, 56), ('AverageFclkFrequencyPostDs', uint16_t, 58), ('AverageUclkFrequencyPreDs', uint16_t, 60), ('AverageUclkFrequencyPostDs', uint16_t, 62), ('AverageGfxActivity', uint16_t, 64), ('AverageUclkActivity', uint16_t, 66), ('CurrSocVoltageOffset', uint8_t, 68), ('CurrGfxVoltageOffset', uint8_t, 69), ('CurrMemVidOffset', uint8_t, 70), ('Padding8', uint8_t, 71), ('AverageSocketPower', uint16_t, 72), ('TemperatureEdge', uint16_t, 74), ('TemperatureHotspot', uint16_t, 76), ('TemperatureMem', uint16_t, 78), ('TemperatureVrGfx', uint16_t, 80), ('TemperatureVrMem0', uint16_t, 82), ('TemperatureVrMem1', uint16_t, 84), ('TemperatureVrSoc', uint16_t, 86), ('TemperatureLiquid0', uint16_t, 88), ('TemperatureLiquid1', uint16_t, 90), ('TemperaturePlx', uint16_t, 92), ('Padding16', uint16_t, 94), ('AccCnt', uint32_t, 96), ('ThrottlingPercentage', c.Array[uint8_t, Literal[20]], 100), ('LinkDpmLevel', uint8_t, 120), ('CurrFanPwm', uint8_t, 121), ('CurrFanSpeed', uint16_t, 122), ('D3HotEntryCountPerMode', c.Array[uint8_t, Literal[4]], 124), ('D3HotExitCountPerMode', c.Array[uint8_t, Literal[4]], 128), ('ArmMsgReceivedCountPerMode', c.Array[uint8_t, Literal[4]], 132), ('EnergyAccumulator', uint32_t, 136), ('AverageVclk0Frequency', uint16_t, 140), ('AverageDclk0Frequency', uint16_t, 142), ('AverageVclk1Frequency', uint16_t, 144), ('AverageDclk1Frequency', uint16_t, 146), ('VcnActivityPercentage', uint16_t, 148), ('PcieRate', uint8_t, 150), ('PcieWidth', uint8_t, 151), ('AverageGfxclkFrequencyTarget', uint16_t, 152), ('Padding16_2', uint16_t, 154)])
@c.record
class SmuMetrics_V3_t(c.Struct):
  SIZE = 164
  CurrClock: c.Array[ctypes.c_uint32, Literal[13]]
  AverageGfxclkFrequencyPreDs: int
  AverageGfxclkFrequencyPostDs: int
  AverageFclkFrequencyPreDs: int
  AverageFclkFrequencyPostDs: int
  AverageUclkFrequencyPreDs: int
  AverageUclkFrequencyPostDs: int
  AverageGfxActivity: int
  AverageUclkActivity: int
  CurrSocVoltageOffset: int
  CurrGfxVoltageOffset: int
  CurrMemVidOffset: int
  Padding8: int
  AverageSocketPower: int
  TemperatureEdge: int
  TemperatureHotspot: int
  TemperatureMem: int
  TemperatureVrGfx: int
  TemperatureVrMem0: int
  TemperatureVrMem1: int
  TemperatureVrSoc: int
  TemperatureLiquid0: int
  TemperatureLiquid1: int
  TemperaturePlx: int
  Padding16: int
  AccCnt: int
  ThrottlingPercentage: c.Array[ctypes.c_ubyte, Literal[20]]
  LinkDpmLevel: int
  CurrFanPwm: int
  CurrFanSpeed: int
  D3HotEntryCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  D3HotExitCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  ArmMsgReceivedCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  EnergyAccumulator: int
  AverageVclk0Frequency: int
  AverageDclk0Frequency: int
  AverageVclk1Frequency: int
  AverageDclk1Frequency: int
  VcnUsagePercentage0: int
  VcnUsagePercentage1: int
  PcieRate: int
  PcieWidth: int
  AverageGfxclkFrequencyTarget: int
  PublicSerialNumLower32: int
  PublicSerialNumUpper32: int
SmuMetrics_V3_t.register_fields([('CurrClock', c.Array[uint32_t, Literal[13]], 0), ('AverageGfxclkFrequencyPreDs', uint16_t, 52), ('AverageGfxclkFrequencyPostDs', uint16_t, 54), ('AverageFclkFrequencyPreDs', uint16_t, 56), ('AverageFclkFrequencyPostDs', uint16_t, 58), ('AverageUclkFrequencyPreDs', uint16_t, 60), ('AverageUclkFrequencyPostDs', uint16_t, 62), ('AverageGfxActivity', uint16_t, 64), ('AverageUclkActivity', uint16_t, 66), ('CurrSocVoltageOffset', uint8_t, 68), ('CurrGfxVoltageOffset', uint8_t, 69), ('CurrMemVidOffset', uint8_t, 70), ('Padding8', uint8_t, 71), ('AverageSocketPower', uint16_t, 72), ('TemperatureEdge', uint16_t, 74), ('TemperatureHotspot', uint16_t, 76), ('TemperatureMem', uint16_t, 78), ('TemperatureVrGfx', uint16_t, 80), ('TemperatureVrMem0', uint16_t, 82), ('TemperatureVrMem1', uint16_t, 84), ('TemperatureVrSoc', uint16_t, 86), ('TemperatureLiquid0', uint16_t, 88), ('TemperatureLiquid1', uint16_t, 90), ('TemperaturePlx', uint16_t, 92), ('Padding16', uint16_t, 94), ('AccCnt', uint32_t, 96), ('ThrottlingPercentage', c.Array[uint8_t, Literal[20]], 100), ('LinkDpmLevel', uint8_t, 120), ('CurrFanPwm', uint8_t, 121), ('CurrFanSpeed', uint16_t, 122), ('D3HotEntryCountPerMode', c.Array[uint8_t, Literal[4]], 124), ('D3HotExitCountPerMode', c.Array[uint8_t, Literal[4]], 128), ('ArmMsgReceivedCountPerMode', c.Array[uint8_t, Literal[4]], 132), ('EnergyAccumulator', uint32_t, 136), ('AverageVclk0Frequency', uint16_t, 140), ('AverageDclk0Frequency', uint16_t, 142), ('AverageVclk1Frequency', uint16_t, 144), ('AverageDclk1Frequency', uint16_t, 146), ('VcnUsagePercentage0', uint16_t, 148), ('VcnUsagePercentage1', uint16_t, 150), ('PcieRate', uint8_t, 152), ('PcieWidth', uint8_t, 153), ('AverageGfxclkFrequencyTarget', uint16_t, 154), ('PublicSerialNumLower32', uint32_t, 156), ('PublicSerialNumUpper32', uint32_t, 160)])
@c.record
class SmuMetrics_V4_t(c.Struct):
  SIZE = 160
  CurrClock: c.Array[ctypes.c_uint32, Literal[13]]
  AverageGfxclkFrequencyPreDs: int
  AverageGfxclkFrequencyPostDs: int
  AverageFclkFrequencyPreDs: int
  AverageFclkFrequencyPostDs: int
  AverageUclkFrequencyPreDs: int
  AverageUclkFrequencyPostDs: int
  AverageGfxActivity: int
  AverageUclkActivity: int
  CurrSocVoltageOffset: int
  CurrGfxVoltageOffset: int
  CurrMemVidOffset: int
  Padding8: int
  AverageSocketPower: int
  TemperatureEdge: int
  TemperatureHotspot: int
  TemperatureMem: int
  TemperatureVrGfx: int
  TemperatureVrMem0: int
  TemperatureVrMem1: int
  TemperatureVrSoc: int
  TemperatureLiquid0: int
  TemperatureLiquid1: int
  TemperaturePlx: int
  Padding16: int
  AccCnt: int
  ThrottlingPercentage: c.Array[ctypes.c_ubyte, Literal[20]]
  LinkDpmLevel: int
  CurrFanPwm: int
  CurrFanSpeed: int
  D3HotEntryCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  D3HotExitCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  ArmMsgReceivedCountPerMode: c.Array[ctypes.c_ubyte, Literal[4]]
  EnergyAccumulator: int
  AverageVclk0Frequency: int
  AverageDclk0Frequency: int
  AverageVclk1Frequency: int
  AverageDclk1Frequency: int
  VcnUsagePercentage0: int
  VcnUsagePercentage1: int
  PcieRate: int
  PcieWidth: int
  AverageGfxclkFrequencyTarget: int
  ApuSTAPMSmartShiftLimit: int
  AverageApuSocketPower: int
  ApuSTAPMLimit: int
  Padding8_2: int
SmuMetrics_V4_t.register_fields([('CurrClock', c.Array[uint32_t, Literal[13]], 0), ('AverageGfxclkFrequencyPreDs', uint16_t, 52), ('AverageGfxclkFrequencyPostDs', uint16_t, 54), ('AverageFclkFrequencyPreDs', uint16_t, 56), ('AverageFclkFrequencyPostDs', uint16_t, 58), ('AverageUclkFrequencyPreDs', uint16_t, 60), ('AverageUclkFrequencyPostDs', uint16_t, 62), ('AverageGfxActivity', uint16_t, 64), ('AverageUclkActivity', uint16_t, 66), ('CurrSocVoltageOffset', uint8_t, 68), ('CurrGfxVoltageOffset', uint8_t, 69), ('CurrMemVidOffset', uint8_t, 70), ('Padding8', uint8_t, 71), ('AverageSocketPower', uint16_t, 72), ('TemperatureEdge', uint16_t, 74), ('TemperatureHotspot', uint16_t, 76), ('TemperatureMem', uint16_t, 78), ('TemperatureVrGfx', uint16_t, 80), ('TemperatureVrMem0', uint16_t, 82), ('TemperatureVrMem1', uint16_t, 84), ('TemperatureVrSoc', uint16_t, 86), ('TemperatureLiquid0', uint16_t, 88), ('TemperatureLiquid1', uint16_t, 90), ('TemperaturePlx', uint16_t, 92), ('Padding16', uint16_t, 94), ('AccCnt', uint32_t, 96), ('ThrottlingPercentage', c.Array[uint8_t, Literal[20]], 100), ('LinkDpmLevel', uint8_t, 120), ('CurrFanPwm', uint8_t, 121), ('CurrFanSpeed', uint16_t, 122), ('D3HotEntryCountPerMode', c.Array[uint8_t, Literal[4]], 124), ('D3HotExitCountPerMode', c.Array[uint8_t, Literal[4]], 128), ('ArmMsgReceivedCountPerMode', c.Array[uint8_t, Literal[4]], 132), ('EnergyAccumulator', uint32_t, 136), ('AverageVclk0Frequency', uint16_t, 140), ('AverageDclk0Frequency', uint16_t, 142), ('AverageVclk1Frequency', uint16_t, 144), ('AverageDclk1Frequency', uint16_t, 146), ('VcnUsagePercentage0', uint16_t, 148), ('VcnUsagePercentage1', uint16_t, 150), ('PcieRate', uint8_t, 152), ('PcieWidth', uint8_t, 153), ('AverageGfxclkFrequencyTarget', uint16_t, 154), ('ApuSTAPMSmartShiftLimit', uint8_t, 156), ('AverageApuSocketPower', uint8_t, 157), ('ApuSTAPMLimit', uint8_t, 158), ('Padding8_2', uint8_t, 159)])
@c.record
class SmuMetricsExternal_t(c.Struct):
  SIZE = 200
  SmuMetrics: SmuMetrics_t
  SmuMetrics_V2: SmuMetrics_V2_t
  SmuMetrics_V3: SmuMetrics_V3_t
  SmuMetrics_V4: SmuMetrics_V4_t
  Spare: c.Array[ctypes.c_uint32, Literal[1]]
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
SmuMetricsExternal_t.register_fields([('SmuMetrics', SmuMetrics_t, 0), ('SmuMetrics_V2', SmuMetrics_V2_t, 0), ('SmuMetrics_V3', SmuMetrics_V3_t, 0), ('SmuMetrics_V4', SmuMetrics_V4_t, 0), ('Spare', c.Array[uint32_t, Literal[1]], 164), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 168)])
@c.record
class WatermarkRowGeneric_t(c.Struct):
  SIZE = 12
  MinClock: int
  MaxClock: int
  MinUclk: int
  MaxUclk: int
  WmSetting: int
  Flags: int
  Padding: c.Array[ctypes.c_ubyte, Literal[2]]
WatermarkRowGeneric_t.register_fields([('MinClock', uint16_t, 0), ('MaxClock', uint16_t, 2), ('MinUclk', uint16_t, 4), ('MaxUclk', uint16_t, 6), ('WmSetting', uint8_t, 8), ('Flags', uint8_t, 9), ('Padding', c.Array[uint8_t, Literal[2]], 10)])
WM_CLOCK_e: dict[int, str] = {(WM_SOCCLK:=0): 'WM_SOCCLK', (WM_DCEFCLK:=1): 'WM_DCEFCLK', (WM_COUNT:=2): 'WM_COUNT'}
WATERMARKS_FLAGS_e: dict[int, str] = {(WATERMARKS_CLOCK_RANGE:=0): 'WATERMARKS_CLOCK_RANGE', (WATERMARKS_DUMMY_PSTATE:=1): 'WATERMARKS_DUMMY_PSTATE', (WATERMARKS_MALL:=2): 'WATERMARKS_MALL', (WATERMARKS_COUNT:=3): 'WATERMARKS_COUNT'}
@c.record
class Watermarks_t(c.Struct):
  SIZE = 96
  WatermarkRow: c.Array[c.Array[WatermarkRowGeneric_t, Literal[4]], Literal[2]]
Watermarks_t.register_fields([('WatermarkRow', c.Array[c.Array[WatermarkRowGeneric_t, Literal[4]], Literal[2]], 0)])
@c.record
class WatermarksExternal_t(c.Struct):
  SIZE = 128
  Watermarks: Watermarks_t
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
WatermarksExternal_t.register_fields([('Watermarks', Watermarks_t, 0), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 96)])
@c.record
class AvfsDebugTable_t(c.Struct):
  SIZE = 804
  avgPsmCount: c.Array[ctypes.c_uint16, Literal[67]]
  minPsmCount: c.Array[ctypes.c_uint16, Literal[67]]
  avgPsmVoltage: c.Array[ctypes.c_float, Literal[67]]
  minPsmVoltage: c.Array[ctypes.c_float, Literal[67]]
AvfsDebugTable_t.register_fields([('avgPsmCount', c.Array[uint16_t, Literal[67]], 0), ('minPsmCount', c.Array[uint16_t, Literal[67]], 134), ('avgPsmVoltage', c.Array[ctypes.c_float, Literal[67]], 268), ('minPsmVoltage', c.Array[ctypes.c_float, Literal[67]], 536)])
@c.record
class AvfsDebugTableExternal_t(c.Struct):
  SIZE = 836
  AvfsDebugTable: AvfsDebugTable_t
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
AvfsDebugTableExternal_t.register_fields([('AvfsDebugTable', AvfsDebugTable_t, 0), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 804)])
@c.record
class AvfsFuseOverride_t(c.Struct):
  SIZE = 212
  AvfsVersion: int
  Padding: int
  AvfsEn: c.Array[ctypes.c_ubyte, Literal[2]]
  OverrideVFT: c.Array[ctypes.c_ubyte, Literal[2]]
  OverrideAvfsGb: c.Array[ctypes.c_ubyte, Literal[2]]
  OverrideTemperatures: c.Array[ctypes.c_ubyte, Literal[2]]
  OverrideVInversion: c.Array[ctypes.c_ubyte, Literal[2]]
  OverrideP2V: c.Array[ctypes.c_ubyte, Literal[2]]
  OverrideP2VCharzFreq: c.Array[ctypes.c_ubyte, Literal[2]]
  VFT0_m1: c.Array[ctypes.c_int32, Literal[2]]
  VFT0_m2: c.Array[ctypes.c_int32, Literal[2]]
  VFT0_b: c.Array[ctypes.c_int32, Literal[2]]
  VFT1_m1: c.Array[ctypes.c_int32, Literal[2]]
  VFT1_m2: c.Array[ctypes.c_int32, Literal[2]]
  VFT1_b: c.Array[ctypes.c_int32, Literal[2]]
  VFT2_m1: c.Array[ctypes.c_int32, Literal[2]]
  VFT2_m2: c.Array[ctypes.c_int32, Literal[2]]
  VFT2_b: c.Array[ctypes.c_int32, Literal[2]]
  AvfsGb0_m1: c.Array[ctypes.c_int32, Literal[2]]
  AvfsGb0_m2: c.Array[ctypes.c_int32, Literal[2]]
  AvfsGb0_b: c.Array[ctypes.c_int32, Literal[2]]
  AcBtcGb_m1: c.Array[ctypes.c_int32, Literal[2]]
  AcBtcGb_m2: c.Array[ctypes.c_int32, Literal[2]]
  AcBtcGb_b: c.Array[ctypes.c_int32, Literal[2]]
  AvfsTempCold: c.Array[ctypes.c_uint32, Literal[2]]
  AvfsTempMid: c.Array[ctypes.c_uint32, Literal[2]]
  AvfsTempHot: c.Array[ctypes.c_uint32, Literal[2]]
  VInversion: c.Array[ctypes.c_uint32, Literal[2]]
  P2V_m1: c.Array[ctypes.c_int32, Literal[2]]
  P2V_m2: c.Array[ctypes.c_int32, Literal[2]]
  P2V_b: c.Array[ctypes.c_int32, Literal[2]]
  P2VCharzFreq: c.Array[ctypes.c_uint32, Literal[2]]
  EnabledAvfsModules: c.Array[ctypes.c_uint32, Literal[3]]
int32_t: TypeAlias = ctypes.c_int32
AvfsFuseOverride_t.register_fields([('AvfsVersion', uint8_t, 0), ('Padding', uint8_t, 1), ('AvfsEn', c.Array[uint8_t, Literal[2]], 2), ('OverrideVFT', c.Array[uint8_t, Literal[2]], 4), ('OverrideAvfsGb', c.Array[uint8_t, Literal[2]], 6), ('OverrideTemperatures', c.Array[uint8_t, Literal[2]], 8), ('OverrideVInversion', c.Array[uint8_t, Literal[2]], 10), ('OverrideP2V', c.Array[uint8_t, Literal[2]], 12), ('OverrideP2VCharzFreq', c.Array[uint8_t, Literal[2]], 14), ('VFT0_m1', c.Array[int32_t, Literal[2]], 16), ('VFT0_m2', c.Array[int32_t, Literal[2]], 24), ('VFT0_b', c.Array[int32_t, Literal[2]], 32), ('VFT1_m1', c.Array[int32_t, Literal[2]], 40), ('VFT1_m2', c.Array[int32_t, Literal[2]], 48), ('VFT1_b', c.Array[int32_t, Literal[2]], 56), ('VFT2_m1', c.Array[int32_t, Literal[2]], 64), ('VFT2_m2', c.Array[int32_t, Literal[2]], 72), ('VFT2_b', c.Array[int32_t, Literal[2]], 80), ('AvfsGb0_m1', c.Array[int32_t, Literal[2]], 88), ('AvfsGb0_m2', c.Array[int32_t, Literal[2]], 96), ('AvfsGb0_b', c.Array[int32_t, Literal[2]], 104), ('AcBtcGb_m1', c.Array[int32_t, Literal[2]], 112), ('AcBtcGb_m2', c.Array[int32_t, Literal[2]], 120), ('AcBtcGb_b', c.Array[int32_t, Literal[2]], 128), ('AvfsTempCold', c.Array[uint32_t, Literal[2]], 136), ('AvfsTempMid', c.Array[uint32_t, Literal[2]], 144), ('AvfsTempHot', c.Array[uint32_t, Literal[2]], 152), ('VInversion', c.Array[uint32_t, Literal[2]], 160), ('P2V_m1', c.Array[int32_t, Literal[2]], 168), ('P2V_m2', c.Array[int32_t, Literal[2]], 176), ('P2V_b', c.Array[int32_t, Literal[2]], 184), ('P2VCharzFreq', c.Array[uint32_t, Literal[2]], 192), ('EnabledAvfsModules', c.Array[uint32_t, Literal[3]], 200)])
@c.record
class AvfsFuseOverrideExternal_t(c.Struct):
  SIZE = 244
  AvfsFuseOverride: AvfsFuseOverride_t
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
AvfsFuseOverrideExternal_t.register_fields([('AvfsFuseOverride', AvfsFuseOverride_t, 0), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 212)])
@c.record
class DpmActivityMonitorCoeffInt_t(c.Struct):
  SIZE = 104
  Gfx_ActiveHystLimit: int
  Gfx_IdleHystLimit: int
  Gfx_FPS: int
  Gfx_MinActiveFreqType: int
  Gfx_BoosterFreqType: int
  Gfx_MinFreqStep: int
  Gfx_MinActiveFreq: int
  Gfx_BoosterFreq: int
  Gfx_PD_Data_time_constant: int
  Gfx_PD_Data_limit_a: int
  Gfx_PD_Data_limit_b: int
  Gfx_PD_Data_limit_c: int
  Gfx_PD_Data_error_coeff: int
  Gfx_PD_Data_error_rate_coeff: int
  Fclk_ActiveHystLimit: int
  Fclk_IdleHystLimit: int
  Fclk_FPS: int
  Fclk_MinActiveFreqType: int
  Fclk_BoosterFreqType: int
  Fclk_MinFreqStep: int
  Fclk_MinActiveFreq: int
  Fclk_BoosterFreq: int
  Fclk_PD_Data_time_constant: int
  Fclk_PD_Data_limit_a: int
  Fclk_PD_Data_limit_b: int
  Fclk_PD_Data_limit_c: int
  Fclk_PD_Data_error_coeff: int
  Fclk_PD_Data_error_rate_coeff: int
  Mem_ActiveHystLimit: int
  Mem_IdleHystLimit: int
  Mem_FPS: int
  Mem_MinActiveFreqType: int
  Mem_BoosterFreqType: int
  Mem_MinFreqStep: int
  Mem_MinActiveFreq: int
  Mem_BoosterFreq: int
  Mem_PD_Data_time_constant: int
  Mem_PD_Data_limit_a: int
  Mem_PD_Data_limit_b: int
  Mem_PD_Data_limit_c: int
  Mem_PD_Data_error_coeff: int
  Mem_PD_Data_error_rate_coeff: int
  Mem_UpThreshold_Limit: int
  Mem_UpHystLimit: int
  Mem_DownHystLimit: int
  Mem_Fps: int
DpmActivityMonitorCoeffInt_t.register_fields([('Gfx_ActiveHystLimit', uint8_t, 0), ('Gfx_IdleHystLimit', uint8_t, 1), ('Gfx_FPS', uint8_t, 2), ('Gfx_MinActiveFreqType', uint8_t, 3), ('Gfx_BoosterFreqType', uint8_t, 4), ('Gfx_MinFreqStep', uint8_t, 5), ('Gfx_MinActiveFreq', uint16_t, 6), ('Gfx_BoosterFreq', uint16_t, 8), ('Gfx_PD_Data_time_constant', uint16_t, 10), ('Gfx_PD_Data_limit_a', uint32_t, 12), ('Gfx_PD_Data_limit_b', uint32_t, 16), ('Gfx_PD_Data_limit_c', uint32_t, 20), ('Gfx_PD_Data_error_coeff', uint32_t, 24), ('Gfx_PD_Data_error_rate_coeff', uint32_t, 28), ('Fclk_ActiveHystLimit', uint8_t, 32), ('Fclk_IdleHystLimit', uint8_t, 33), ('Fclk_FPS', uint8_t, 34), ('Fclk_MinActiveFreqType', uint8_t, 35), ('Fclk_BoosterFreqType', uint8_t, 36), ('Fclk_MinFreqStep', uint8_t, 37), ('Fclk_MinActiveFreq', uint16_t, 38), ('Fclk_BoosterFreq', uint16_t, 40), ('Fclk_PD_Data_time_constant', uint16_t, 42), ('Fclk_PD_Data_limit_a', uint32_t, 44), ('Fclk_PD_Data_limit_b', uint32_t, 48), ('Fclk_PD_Data_limit_c', uint32_t, 52), ('Fclk_PD_Data_error_coeff', uint32_t, 56), ('Fclk_PD_Data_error_rate_coeff', uint32_t, 60), ('Mem_ActiveHystLimit', uint8_t, 64), ('Mem_IdleHystLimit', uint8_t, 65), ('Mem_FPS', uint8_t, 66), ('Mem_MinActiveFreqType', uint8_t, 67), ('Mem_BoosterFreqType', uint8_t, 68), ('Mem_MinFreqStep', uint8_t, 69), ('Mem_MinActiveFreq', uint16_t, 70), ('Mem_BoosterFreq', uint16_t, 72), ('Mem_PD_Data_time_constant', uint16_t, 74), ('Mem_PD_Data_limit_a', uint32_t, 76), ('Mem_PD_Data_limit_b', uint32_t, 80), ('Mem_PD_Data_limit_c', uint32_t, 84), ('Mem_PD_Data_error_coeff', uint32_t, 88), ('Mem_PD_Data_error_rate_coeff', uint32_t, 92), ('Mem_UpThreshold_Limit', uint32_t, 96), ('Mem_UpHystLimit', uint8_t, 100), ('Mem_DownHystLimit', uint8_t, 101), ('Mem_Fps', uint16_t, 102)])
@c.record
class DpmActivityMonitorCoeffIntExternal_t(c.Struct):
  SIZE = 136
  DpmActivityMonitorCoeffInt: DpmActivityMonitorCoeffInt_t
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
DpmActivityMonitorCoeffIntExternal_t.register_fields([('DpmActivityMonitorCoeffInt', DpmActivityMonitorCoeffInt_t, 0), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 104)])
@c.record
class RlcPaceFlopsPerByteOverride_t(c.Struct):
  SIZE = 64
  FlopsPerByteTable: c.Array[ctypes.c_float, Literal[16]]
RlcPaceFlopsPerByteOverride_t.register_fields([('FlopsPerByteTable', c.Array[ctypes.c_float, Literal[16]], 0)])
@c.record
class RlcPaceFlopsPerByteOverrideExternal_t(c.Struct):
  SIZE = 96
  RlcPaceFlopsPerByteOverride: RlcPaceFlopsPerByteOverride_t
  MmHubPadding: c.Array[ctypes.c_uint32, Literal[8]]
RlcPaceFlopsPerByteOverrideExternal_t.register_fields([('RlcPaceFlopsPerByteOverride', RlcPaceFlopsPerByteOverride_t, 0), ('MmHubPadding', c.Array[uint32_t, Literal[8]], 64)])
@c.record
class struct_smu_hw_power_state(c.Struct):
  SIZE = 4
  magic: int
struct_smu_hw_power_state.register_fields([('magic', ctypes.c_uint32, 0)])
class struct_smu_power_state(c.Struct): pass
enum_smu_state_ui_label: dict[int, str] = {(SMU_STATE_UI_LABEL_NONE:=0): 'SMU_STATE_UI_LABEL_NONE', (SMU_STATE_UI_LABEL_BATTERY:=1): 'SMU_STATE_UI_LABEL_BATTERY', (SMU_STATE_UI_TABEL_MIDDLE_LOW:=2): 'SMU_STATE_UI_TABEL_MIDDLE_LOW', (SMU_STATE_UI_LABEL_BALLANCED:=3): 'SMU_STATE_UI_LABEL_BALLANCED', (SMU_STATE_UI_LABEL_MIDDLE_HIGHT:=4): 'SMU_STATE_UI_LABEL_MIDDLE_HIGHT', (SMU_STATE_UI_LABEL_PERFORMANCE:=5): 'SMU_STATE_UI_LABEL_PERFORMANCE', (SMU_STATE_UI_LABEL_BACO:=6): 'SMU_STATE_UI_LABEL_BACO'}
enum_smu_state_classification_flag: dict[int, str] = {(SMU_STATE_CLASSIFICATION_FLAG_BOOT:=1): 'SMU_STATE_CLASSIFICATION_FLAG_BOOT', (SMU_STATE_CLASSIFICATION_FLAG_THERMAL:=2): 'SMU_STATE_CLASSIFICATION_FLAG_THERMAL', (SMU_STATE_CLASSIFICATIN_FLAG_LIMITED_POWER_SOURCE:=4): 'SMU_STATE_CLASSIFICATIN_FLAG_LIMITED_POWER_SOURCE', (SMU_STATE_CLASSIFICATION_FLAG_RESET:=8): 'SMU_STATE_CLASSIFICATION_FLAG_RESET', (SMU_STATE_CLASSIFICATION_FLAG_FORCED:=16): 'SMU_STATE_CLASSIFICATION_FLAG_FORCED', (SMU_STATE_CLASSIFICATION_FLAG_USER_3D_PERFORMANCE:=32): 'SMU_STATE_CLASSIFICATION_FLAG_USER_3D_PERFORMANCE', (SMU_STATE_CLASSIFICATION_FLAG_USER_2D_PERFORMANCE:=64): 'SMU_STATE_CLASSIFICATION_FLAG_USER_2D_PERFORMANCE', (SMU_STATE_CLASSIFICATION_FLAG_3D_PERFORMANCE:=128): 'SMU_STATE_CLASSIFICATION_FLAG_3D_PERFORMANCE', (SMU_STATE_CLASSIFICATION_FLAG_AC_OVERDIRVER_TEMPLATE:=256): 'SMU_STATE_CLASSIFICATION_FLAG_AC_OVERDIRVER_TEMPLATE', (SMU_STATE_CLASSIFICATION_FLAG_UVD:=512): 'SMU_STATE_CLASSIFICATION_FLAG_UVD', (SMU_STATE_CLASSIFICATION_FLAG_3D_PERFORMANCE_LOW:=1024): 'SMU_STATE_CLASSIFICATION_FLAG_3D_PERFORMANCE_LOW', (SMU_STATE_CLASSIFICATION_FLAG_ACPI:=2048): 'SMU_STATE_CLASSIFICATION_FLAG_ACPI', (SMU_STATE_CLASSIFICATION_FLAG_HD2:=4096): 'SMU_STATE_CLASSIFICATION_FLAG_HD2', (SMU_STATE_CLASSIFICATION_FLAG_UVD_HD:=8192): 'SMU_STATE_CLASSIFICATION_FLAG_UVD_HD', (SMU_STATE_CLASSIFICATION_FLAG_UVD_SD:=16384): 'SMU_STATE_CLASSIFICATION_FLAG_UVD_SD', (SMU_STATE_CLASSIFICATION_FLAG_USER_DC_PERFORMANCE:=32768): 'SMU_STATE_CLASSIFICATION_FLAG_USER_DC_PERFORMANCE', (SMU_STATE_CLASSIFICATION_FLAG_DC_OVERDIRVER_TEMPLATE:=65536): 'SMU_STATE_CLASSIFICATION_FLAG_DC_OVERDIRVER_TEMPLATE', (SMU_STATE_CLASSIFICATION_FLAG_BACO:=131072): 'SMU_STATE_CLASSIFICATION_FLAG_BACO', (SMU_STATE_CLASSIFICATIN_FLAG_LIMITED_POWER_SOURCE2:=262144): 'SMU_STATE_CLASSIFICATIN_FLAG_LIMITED_POWER_SOURCE2', (SMU_STATE_CLASSIFICATION_FLAG_ULV:=524288): 'SMU_STATE_CLASSIFICATION_FLAG_ULV', (SMU_STATE_CLASSIFICATION_FLAG_UVD_MVC:=1048576): 'SMU_STATE_CLASSIFICATION_FLAG_UVD_MVC'}
@c.record
class struct_smu_state_classification_block(c.Struct):
  SIZE = 16
  ui_label: int
  flags: int
  bios_index: int
  temporary_state: bool
  to_be_deleted: bool
struct_smu_state_classification_block.register_fields([('ui_label', ctypes.c_uint32, 0), ('flags', ctypes.c_uint32, 4), ('bios_index', ctypes.c_int32, 8), ('temporary_state', ctypes.c_bool, 12), ('to_be_deleted', ctypes.c_bool, 13)])
@c.record
class struct_smu_state_pcie_block(c.Struct):
  SIZE = 4
  lanes: int
struct_smu_state_pcie_block.register_fields([('lanes', ctypes.c_uint32, 0)])
enum_smu_refreshrate_source: dict[int, str] = {(SMU_REFRESHRATE_SOURCE_EDID:=0): 'SMU_REFRESHRATE_SOURCE_EDID', (SMU_REFRESHRATE_SOURCE_EXPLICIT:=1): 'SMU_REFRESHRATE_SOURCE_EXPLICIT'}
@c.record
class struct_smu_state_display_block(c.Struct):
  SIZE = 20
  disable_frame_modulation: bool
  limit_refreshrate: bool
  refreshrate_source: int
  explicit_refreshrate: int
  edid_refreshrate_index: int
  enable_vari_bright: bool
struct_smu_state_display_block.register_fields([('disable_frame_modulation', ctypes.c_bool, 0), ('limit_refreshrate', ctypes.c_bool, 1), ('refreshrate_source', ctypes.c_uint32, 4), ('explicit_refreshrate', ctypes.c_int32, 8), ('edid_refreshrate_index', ctypes.c_int32, 12), ('enable_vari_bright', ctypes.c_bool, 16)])
@c.record
class struct_smu_state_memory_block(c.Struct):
  SIZE = 5
  dll_off: bool
  m3arb: int
  unused: c.Array[ctypes.c_ubyte, Literal[3]]
struct_smu_state_memory_block.register_fields([('dll_off', ctypes.c_bool, 0), ('m3arb', uint8_t, 1), ('unused', c.Array[uint8_t, Literal[3]], 2)])
@c.record
class struct_smu_state_software_algorithm_block(c.Struct):
  SIZE = 2
  disable_load_balancing: bool
  enable_sleep_for_timestamps: bool
struct_smu_state_software_algorithm_block.register_fields([('disable_load_balancing', ctypes.c_bool, 0), ('enable_sleep_for_timestamps', ctypes.c_bool, 1)])
@c.record
class struct_smu_temperature_range(c.Struct):
  SIZE = 44
  min: int
  max: int
  edge_emergency_max: int
  hotspot_min: int
  hotspot_crit_max: int
  hotspot_emergency_max: int
  mem_min: int
  mem_crit_max: int
  mem_emergency_max: int
  software_shutdown_temp: int
  software_shutdown_temp_offset: int
struct_smu_temperature_range.register_fields([('min', ctypes.c_int32, 0), ('max', ctypes.c_int32, 4), ('edge_emergency_max', ctypes.c_int32, 8), ('hotspot_min', ctypes.c_int32, 12), ('hotspot_crit_max', ctypes.c_int32, 16), ('hotspot_emergency_max', ctypes.c_int32, 20), ('mem_min', ctypes.c_int32, 24), ('mem_crit_max', ctypes.c_int32, 28), ('mem_emergency_max', ctypes.c_int32, 32), ('software_shutdown_temp', ctypes.c_int32, 36), ('software_shutdown_temp_offset', ctypes.c_int32, 40)])
@c.record
class struct_smu_state_validation_block(c.Struct):
  SIZE = 3
  single_display_only: bool
  disallow_on_dc: bool
  supported_power_levels: int
struct_smu_state_validation_block.register_fields([('single_display_only', ctypes.c_bool, 0), ('disallow_on_dc', ctypes.c_bool, 1), ('supported_power_levels', uint8_t, 2)])
@c.record
class struct_smu_uvd_clocks(c.Struct):
  SIZE = 8
  vclk: int
  dclk: int
struct_smu_uvd_clocks.register_fields([('vclk', uint32_t, 0), ('dclk', uint32_t, 4)])
enum_smu_power_src_type: dict[int, str] = {(SMU_POWER_SOURCE_AC:=0): 'SMU_POWER_SOURCE_AC', (SMU_POWER_SOURCE_DC:=1): 'SMU_POWER_SOURCE_DC', (SMU_POWER_SOURCE_COUNT:=2): 'SMU_POWER_SOURCE_COUNT'}
enum_smu_ppt_limit_type: dict[int, str] = {(SMU_DEFAULT_PPT_LIMIT:=0): 'SMU_DEFAULT_PPT_LIMIT', (SMU_FAST_PPT_LIMIT:=1): 'SMU_FAST_PPT_LIMIT'}
enum_smu_ppt_limit_level: dict[int, str] = {(SMU_PPT_LIMIT_MIN:=-1): 'SMU_PPT_LIMIT_MIN', (SMU_PPT_LIMIT_CURRENT:=0): 'SMU_PPT_LIMIT_CURRENT', (SMU_PPT_LIMIT_DEFAULT:=1): 'SMU_PPT_LIMIT_DEFAULT', (SMU_PPT_LIMIT_MAX:=2): 'SMU_PPT_LIMIT_MAX'}
enum_smu_memory_pool_size: dict[int, str] = {(SMU_MEMORY_POOL_SIZE_ZERO:=0): 'SMU_MEMORY_POOL_SIZE_ZERO', (SMU_MEMORY_POOL_SIZE_256_MB:=268435456): 'SMU_MEMORY_POOL_SIZE_256_MB', (SMU_MEMORY_POOL_SIZE_512_MB:=536870912): 'SMU_MEMORY_POOL_SIZE_512_MB', (SMU_MEMORY_POOL_SIZE_1_GB:=1073741824): 'SMU_MEMORY_POOL_SIZE_1_GB', (SMU_MEMORY_POOL_SIZE_2_GB:=2147483648): 'SMU_MEMORY_POOL_SIZE_2_GB'}
enum_smu_clk_type: dict[int, str] = {(SMU_GFXCLK:=0): 'SMU_GFXCLK', (SMU_VCLK:=1): 'SMU_VCLK', (SMU_DCLK:=2): 'SMU_DCLK', (SMU_VCLK1:=3): 'SMU_VCLK1', (SMU_DCLK1:=4): 'SMU_DCLK1', (SMU_ECLK:=5): 'SMU_ECLK', (SMU_SOCCLK:=6): 'SMU_SOCCLK', (SMU_UCLK:=7): 'SMU_UCLK', (SMU_DCEFCLK:=8): 'SMU_DCEFCLK', (SMU_DISPCLK:=9): 'SMU_DISPCLK', (SMU_PIXCLK:=10): 'SMU_PIXCLK', (SMU_PHYCLK:=11): 'SMU_PHYCLK', (SMU_FCLK:=12): 'SMU_FCLK', (SMU_SCLK:=13): 'SMU_SCLK', (SMU_MCLK:=14): 'SMU_MCLK', (SMU_PCIE:=15): 'SMU_PCIE', (SMU_LCLK:=16): 'SMU_LCLK', (SMU_OD_CCLK:=17): 'SMU_OD_CCLK', (SMU_OD_SCLK:=18): 'SMU_OD_SCLK', (SMU_OD_MCLK:=19): 'SMU_OD_MCLK', (SMU_OD_VDDC_CURVE:=20): 'SMU_OD_VDDC_CURVE', (SMU_OD_RANGE:=21): 'SMU_OD_RANGE', (SMU_OD_VDDGFX_OFFSET:=22): 'SMU_OD_VDDGFX_OFFSET', (SMU_OD_FAN_CURVE:=23): 'SMU_OD_FAN_CURVE', (SMU_OD_ACOUSTIC_LIMIT:=24): 'SMU_OD_ACOUSTIC_LIMIT', (SMU_OD_ACOUSTIC_TARGET:=25): 'SMU_OD_ACOUSTIC_TARGET', (SMU_OD_FAN_TARGET_TEMPERATURE:=26): 'SMU_OD_FAN_TARGET_TEMPERATURE', (SMU_OD_FAN_MINIMUM_PWM:=27): 'SMU_OD_FAN_MINIMUM_PWM', (SMU_CLK_COUNT:=28): 'SMU_CLK_COUNT'}
@c.record
class struct_smu_user_dpm_profile(c.Struct):
  SIZE = 140
  fan_mode: int
  power_limit: int
  fan_speed_pwm: int
  fan_speed_rpm: int
  flags: int
  user_od: int
  clk_mask: c.Array[ctypes.c_uint32, Literal[28]]
  clk_dependency: int
struct_smu_user_dpm_profile.register_fields([('fan_mode', uint32_t, 0), ('power_limit', uint32_t, 4), ('fan_speed_pwm', uint32_t, 8), ('fan_speed_rpm', uint32_t, 12), ('flags', uint32_t, 16), ('user_od', uint32_t, 20), ('clk_mask', c.Array[uint32_t, Literal[28]], 24), ('clk_dependency', uint32_t, 136)])
@c.record
class struct_smu_table(c.Struct):
  SIZE = 48
  size: int
  align: int
  domain: int
  mc_address: int
  cpu_addr: ctypes.c_void_p
  bo: c.POINTER[struct_amdgpu_bo]
  version: int
class struct_amdgpu_bo(c.Struct): pass
struct_smu_table.register_fields([('size', uint64_t, 0), ('align', uint32_t, 8), ('domain', uint8_t, 12), ('mc_address', uint64_t, 16), ('cpu_addr', ctypes.c_void_p, 24), ('bo', c.POINTER[struct_amdgpu_bo], 32), ('version', uint32_t, 40)])
enum_smu_perf_level_designation: dict[int, str] = {(PERF_LEVEL_ACTIVITY:=0): 'PERF_LEVEL_ACTIVITY', (PERF_LEVEL_POWER_CONTAINMENT:=1): 'PERF_LEVEL_POWER_CONTAINMENT'}
@c.record
class struct_smu_performance_level(c.Struct):
  SIZE = 24
  core_clock: int
  memory_clock: int
  vddc: int
  vddci: int
  non_local_mem_freq: int
  non_local_mem_width: int
struct_smu_performance_level.register_fields([('core_clock', uint32_t, 0), ('memory_clock', uint32_t, 4), ('vddc', uint32_t, 8), ('vddci', uint32_t, 12), ('non_local_mem_freq', uint32_t, 16), ('non_local_mem_width', uint32_t, 20)])
@c.record
class struct_smu_clock_info(c.Struct):
  SIZE = 24
  min_mem_clk: int
  max_mem_clk: int
  min_eng_clk: int
  max_eng_clk: int
  min_bus_bandwidth: int
  max_bus_bandwidth: int
struct_smu_clock_info.register_fields([('min_mem_clk', uint32_t, 0), ('max_mem_clk', uint32_t, 4), ('min_eng_clk', uint32_t, 8), ('max_eng_clk', uint32_t, 12), ('min_bus_bandwidth', uint32_t, 16), ('max_bus_bandwidth', uint32_t, 20)])
@c.record
class struct_smu_bios_boot_up_values(c.Struct):
  SIZE = 68
  revision: int
  gfxclk: int
  uclk: int
  socclk: int
  dcefclk: int
  eclk: int
  vclk: int
  dclk: int
  vddc: int
  vddci: int
  mvddc: int
  vdd_gfx: int
  cooling_id: int
  pp_table_id: int
  format_revision: int
  content_revision: int
  fclk: int
  lclk: int
  firmware_caps: int
struct_smu_bios_boot_up_values.register_fields([('revision', uint32_t, 0), ('gfxclk', uint32_t, 4), ('uclk', uint32_t, 8), ('socclk', uint32_t, 12), ('dcefclk', uint32_t, 16), ('eclk', uint32_t, 20), ('vclk', uint32_t, 24), ('dclk', uint32_t, 28), ('vddc', uint16_t, 32), ('vddci', uint16_t, 34), ('mvddc', uint16_t, 36), ('vdd_gfx', uint16_t, 38), ('cooling_id', uint8_t, 40), ('pp_table_id', uint32_t, 44), ('format_revision', uint32_t, 48), ('content_revision', uint32_t, 52), ('fclk', uint32_t, 56), ('lclk', uint32_t, 60), ('firmware_caps', uint32_t, 64)])
enum_smu_table_id: dict[int, str] = {(SMU_TABLE_PPTABLE:=0): 'SMU_TABLE_PPTABLE', (SMU_TABLE_WATERMARKS:=1): 'SMU_TABLE_WATERMARKS', (SMU_TABLE_CUSTOM_DPM:=2): 'SMU_TABLE_CUSTOM_DPM', (SMU_TABLE_DPMCLOCKS:=3): 'SMU_TABLE_DPMCLOCKS', (SMU_TABLE_AVFS:=4): 'SMU_TABLE_AVFS', (SMU_TABLE_AVFS_PSM_DEBUG:=5): 'SMU_TABLE_AVFS_PSM_DEBUG', (SMU_TABLE_AVFS_FUSE_OVERRIDE:=6): 'SMU_TABLE_AVFS_FUSE_OVERRIDE', (SMU_TABLE_PMSTATUSLOG:=7): 'SMU_TABLE_PMSTATUSLOG', (SMU_TABLE_SMU_METRICS:=8): 'SMU_TABLE_SMU_METRICS', (SMU_TABLE_DRIVER_SMU_CONFIG:=9): 'SMU_TABLE_DRIVER_SMU_CONFIG', (SMU_TABLE_ACTIVITY_MONITOR_COEFF:=10): 'SMU_TABLE_ACTIVITY_MONITOR_COEFF', (SMU_TABLE_OVERDRIVE:=11): 'SMU_TABLE_OVERDRIVE', (SMU_TABLE_I2C_COMMANDS:=12): 'SMU_TABLE_I2C_COMMANDS', (SMU_TABLE_PACE:=13): 'SMU_TABLE_PACE', (SMU_TABLE_ECCINFO:=14): 'SMU_TABLE_ECCINFO', (SMU_TABLE_COMBO_PPTABLE:=15): 'SMU_TABLE_COMBO_PPTABLE', (SMU_TABLE_WIFIBAND:=16): 'SMU_TABLE_WIFIBAND', (SMU_TABLE_COUNT:=17): 'SMU_TABLE_COUNT'}
PPSMC_VERSION = 0x1
PPSMC_Result_OK = 0x1
PPSMC_Result_Failed = 0xFF
PPSMC_Result_UnknownCmd = 0xFE
PPSMC_Result_CmdRejectedPrereq = 0xFD
PPSMC_Result_CmdRejectedBusy = 0xFC
PPSMC_MSG_TestMessage = 0x1
PPSMC_MSG_GetSmuVersion = 0x2
PPSMC_MSG_GetDriverIfVersion = 0x3
PPSMC_MSG_SetAllowedFeaturesMaskLow = 0x4
PPSMC_MSG_SetAllowedFeaturesMaskHigh = 0x5
PPSMC_MSG_EnableAllSmuFeatures = 0x6
PPSMC_MSG_DisableAllSmuFeatures = 0x7
PPSMC_MSG_EnableSmuFeaturesLow = 0x8
PPSMC_MSG_EnableSmuFeaturesHigh = 0x9
PPSMC_MSG_DisableSmuFeaturesLow = 0xA
PPSMC_MSG_DisableSmuFeaturesHigh = 0xB
PPSMC_MSG_GetRunningSmuFeaturesLow = 0xC
PPSMC_MSG_GetRunningSmuFeaturesHigh = 0xD
PPSMC_MSG_SetDriverDramAddrHigh = 0xE
PPSMC_MSG_SetDriverDramAddrLow = 0xF
PPSMC_MSG_SetToolsDramAddrHigh = 0x10
PPSMC_MSG_SetToolsDramAddrLow = 0x11
PPSMC_MSG_TransferTableSmu2Dram = 0x12
PPSMC_MSG_TransferTableDram2Smu = 0x13
PPSMC_MSG_UseDefaultPPTable = 0x14
PPSMC_MSG_EnterBaco = 0x15
PPSMC_MSG_ExitBaco = 0x16
PPSMC_MSG_ArmD3 = 0x17
PPSMC_MSG_BacoAudioD3PME = 0x18
PPSMC_MSG_SetSoftMinByFreq = 0x19
PPSMC_MSG_SetSoftMaxByFreq = 0x1A
PPSMC_MSG_SetHardMinByFreq = 0x1B
PPSMC_MSG_SetHardMaxByFreq = 0x1C
PPSMC_MSG_GetMinDpmFreq = 0x1D
PPSMC_MSG_GetMaxDpmFreq = 0x1E
PPSMC_MSG_GetDpmFreqByIndex = 0x1F
PPSMC_MSG_OverridePcieParameters = 0x20
PPSMC_MSG_DramLogSetDramAddrHigh = 0x21
PPSMC_MSG_SetWorkloadMask = 0x22
PPSMC_MSG_SetUclkFastSwitch = 0x23
PPSMC_MSG_GetVoltageByDpm = 0x24
PPSMC_MSG_SetVideoFps = 0x25
PPSMC_MSG_GetDcModeMaxDpmFreq = 0x26
PPSMC_MSG_DramLogSetDramAddrLow = 0x27
PPSMC_MSG_AllowGfxOff = 0x28
PPSMC_MSG_DisallowGfxOff = 0x29
PPSMC_MSG_PowerUpVcn = 0x2A
PPSMC_MSG_PowerDownVcn = 0x2B
PPSMC_MSG_PowerUpJpeg = 0x2C
PPSMC_MSG_PowerDownJpeg = 0x2D
PPSMC_MSG_PrepareMp1ForUnload = 0x2E
PPSMC_MSG_DramLogSetDramSize = 0x2F
PPSMC_MSG_Mode1Reset = 0x30
PPSMC_MSG_SetSystemVirtualDramAddrHigh = 0x31
PPSMC_MSG_SetPptLimit = 0x32
PPSMC_MSG_GetPptLimit = 0x33
PPSMC_MSG_ReenableAcDcInterrupt = 0x34
PPSMC_MSG_NotifyPowerSource = 0x35
PPSMC_MSG_RunDcBtc = 0x36
PPSMC_MSG_SetSystemVirtualDramAddrLow = 0x38
PPSMC_MSG_SetMemoryChannelEnable = 0x39
PPSMC_MSG_SetDramBitWidth = 0x3A
PPSMC_MSG_SetGeminiMode = 0x3B
PPSMC_MSG_SetGeminiApertureHigh = 0x3C
PPSMC_MSG_SetGeminiApertureLow = 0x3D
PPSMC_MSG_SetTemperatureInputSelect = 0x3E
PPSMC_MSG_SetFwDstatesMask = 0x3F
PPSMC_MSG_SetThrottlerMask = 0x40
PPSMC_MSG_SetExternalClientDfCstateAllow = 0x41
PPSMC_MSG_EnableOutOfBandMonTesting = 0x42
PPSMC_MSG_SetMGpuFanBoostLimitRpm = 0x43
PPSMC_MSG_SetNumBadHbmPagesRetired = 0x44
PPSMC_MSG_SetGpoFeaturePMask = 0x45
PPSMC_MSG_SetSMBUSInterrupt = 0x46
PPSMC_MSG_DisallowGpo = 0x56
PPSMC_MSG_Enable2ndUSB20Port = 0x57
PPSMC_MSG_DriverMode2Reset = 0x5D
PPSMC_Message_Count = 0x5E
SMU11_DRIVER_IF_VERSION = 0x40
PPTABLE_Sienna_Cichlid_SMU_VERSION = 7
NUM_GFXCLK_DPM_LEVELS = 16
NUM_SMNCLK_DPM_LEVELS = 2
NUM_SOCCLK_DPM_LEVELS = 8
NUM_MP0CLK_DPM_LEVELS = 2
NUM_DCLK_DPM_LEVELS = 8
NUM_VCLK_DPM_LEVELS = 8
NUM_DCEFCLK_DPM_LEVELS = 8
NUM_PHYCLK_DPM_LEVELS = 8
NUM_DISPCLK_DPM_LEVELS = 8
NUM_PIXCLK_DPM_LEVELS = 8
NUM_DTBCLK_DPM_LEVELS = 8
NUM_UCLK_DPM_LEVELS = 4
NUM_MP1CLK_DPM_LEVELS = 2
NUM_LINK_LEVELS = 2
NUM_FCLK_DPM_LEVELS = 8
NUM_XGMI_LEVELS = 2
NUM_XGMI_PSTATE_LEVELS = 4
NUM_OD_FAN_MAX_POINTS = 6
MAX_GFXCLK_DPM_LEVEL = (NUM_GFXCLK_DPM_LEVELS  - 1)
MAX_SMNCLK_DPM_LEVEL = (NUM_SMNCLK_DPM_LEVELS  - 1)
MAX_SOCCLK_DPM_LEVEL = (NUM_SOCCLK_DPM_LEVELS  - 1)
MAX_MP0CLK_DPM_LEVEL = (NUM_MP0CLK_DPM_LEVELS  - 1)
MAX_DCLK_DPM_LEVEL = (NUM_DCLK_DPM_LEVELS    - 1)
MAX_VCLK_DPM_LEVEL = (NUM_VCLK_DPM_LEVELS    - 1)
MAX_DCEFCLK_DPM_LEVEL = (NUM_DCEFCLK_DPM_LEVELS - 1)
MAX_DISPCLK_DPM_LEVEL = (NUM_DISPCLK_DPM_LEVELS - 1)
MAX_PIXCLK_DPM_LEVEL = (NUM_PIXCLK_DPM_LEVELS  - 1)
MAX_PHYCLK_DPM_LEVEL = (NUM_PHYCLK_DPM_LEVELS  - 1)
MAX_DTBCLK_DPM_LEVEL = (NUM_DTBCLK_DPM_LEVELS  - 1)
MAX_UCLK_DPM_LEVEL = (NUM_UCLK_DPM_LEVELS    - 1)
MAX_MP1CLK_DPM_LEVEL = (NUM_MP1CLK_DPM_LEVELS  - 1)
MAX_LINK_LEVEL = (NUM_LINK_LEVELS        - 1)
MAX_FCLK_DPM_LEVEL = (NUM_FCLK_DPM_LEVELS    - 1)
PPSMC_GeminiModeNone = 0
PPSMC_GeminiModeMaster = 1
PPSMC_GeminiModeSlave = 2
FEATURE_DPM_PREFETCHER_BIT = 0
FEATURE_DPM_GFXCLK_BIT = 1
FEATURE_DPM_GFX_GPO_BIT = 2
FEATURE_DPM_UCLK_BIT = 3
FEATURE_DPM_FCLK_BIT = 4
FEATURE_DPM_SOCCLK_BIT = 5
FEATURE_DPM_MP0CLK_BIT = 6
FEATURE_DPM_LINK_BIT = 7
FEATURE_DPM_DCEFCLK_BIT = 8
FEATURE_DPM_XGMI_BIT = 9
FEATURE_MEM_VDDCI_SCALING_BIT = 10
FEATURE_MEM_MVDD_SCALING_BIT = 11
FEATURE_DS_GFXCLK_BIT = 12
FEATURE_DS_SOCCLK_BIT = 13
FEATURE_DS_FCLK_BIT = 14
FEATURE_DS_LCLK_BIT = 15
FEATURE_DS_DCEFCLK_BIT = 16
FEATURE_DS_UCLK_BIT = 17
FEATURE_GFX_ULV_BIT = 18
FEATURE_FW_DSTATE_BIT = 19
FEATURE_GFXOFF_BIT = 20
FEATURE_BACO_BIT = 21
FEATURE_MM_DPM_PG_BIT = 22
FEATURE_SPARE_23_BIT = 23
FEATURE_PPT_BIT = 24
FEATURE_TDC_BIT = 25
FEATURE_APCC_PLUS_BIT = 26
FEATURE_GTHR_BIT = 27
FEATURE_ACDC_BIT = 28
FEATURE_VR0HOT_BIT = 29
FEATURE_VR1HOT_BIT = 30
FEATURE_FW_CTF_BIT = 31
FEATURE_FAN_CONTROL_BIT = 32
FEATURE_THERMAL_BIT = 33
FEATURE_GFX_DCS_BIT = 34
FEATURE_RM_BIT = 35
FEATURE_LED_DISPLAY_BIT = 36
FEATURE_GFX_SS_BIT = 37
FEATURE_OUT_OF_BAND_MONITOR_BIT = 38
FEATURE_TEMP_DEPENDENT_VMIN_BIT = 39
FEATURE_MMHUB_PG_BIT = 40
FEATURE_ATHUB_PG_BIT = 41
FEATURE_APCC_DFLL_BIT = 42
FEATURE_DF_SUPERV_BIT = 43
FEATURE_RSMU_SMN_CG_BIT = 44
FEATURE_DF_CSTATE_BIT = 45
FEATURE_2_STEP_PSTATE_BIT = 46
FEATURE_SMNCLK_DPM_BIT = 47
FEATURE_PERLINK_GMIDOWN_BIT = 48
FEATURE_GFX_EDC_BIT = 49
FEATURE_GFX_PER_PART_VMIN_BIT = 50
FEATURE_SMART_SHIFT_BIT = 51
FEATURE_APT_BIT = 52
FEATURE_SPARE_53_BIT = 53
FEATURE_SPARE_54_BIT = 54
FEATURE_SPARE_55_BIT = 55
FEATURE_SPARE_56_BIT = 56
FEATURE_SPARE_57_BIT = 57
FEATURE_SPARE_58_BIT = 58
FEATURE_SPARE_59_BIT = 59
FEATURE_SPARE_60_BIT = 60
FEATURE_SPARE_61_BIT = 61
FEATURE_SPARE_62_BIT = 62
FEATURE_SPARE_63_BIT = 63
NUM_FEATURES = 64
DPM_OVERRIDE_DISABLE_FCLK_PID = 0x00000001
DPM_OVERRIDE_DISABLE_UCLK_PID = 0x00000002
DPM_OVERRIDE_DISABLE_VOLT_LINK_VCN_FCLK = 0x00000004
DPM_OVERRIDE_ENABLE_FREQ_LINK_VCLK_FCLK = 0x00000008
DPM_OVERRIDE_ENABLE_FREQ_LINK_DCLK_FCLK = 0x00000010
DPM_OVERRIDE_ENABLE_FREQ_LINK_GFXCLK_SOCCLK = 0x00000020
DPM_OVERRIDE_ENABLE_FREQ_LINK_GFXCLK_UCLK = 0x00000040
DPM_OVERRIDE_DISABLE_VOLT_LINK_DCE_FCLK = 0x00000080
DPM_OVERRIDE_DISABLE_VOLT_LINK_MP0_SOCCLK = 0x00000100
DPM_OVERRIDE_DISABLE_DFLL_PLL_SHUTDOWN = 0x00000200
DPM_OVERRIDE_DISABLE_MEMORY_TEMPERATURE_READ = 0x00000400
DPM_OVERRIDE_DISABLE_VOLT_LINK_VCN_DCEFCLK = 0x00000800
DPM_OVERRIDE_DISABLE_FAST_FCLK_TIMER = 0x00001000
DPM_OVERRIDE_DISABLE_VCN_PG = 0x00002000
DPM_OVERRIDE_DISABLE_FMAX_VMAX = 0x00004000
DPM_OVERRIDE_ENABLE_eGPU_USB_WA = 0x00008000
VR_MAPPING_VR_SELECT_MASK = 0x01
VR_MAPPING_VR_SELECT_SHIFT = 0x00
VR_MAPPING_PLANE_SELECT_MASK = 0x02
VR_MAPPING_PLANE_SELECT_SHIFT = 0x01
PSI_SEL_VR0_PLANE0_PSI0 = 0x01
PSI_SEL_VR0_PLANE0_PSI1 = 0x02
PSI_SEL_VR0_PLANE1_PSI0 = 0x04
PSI_SEL_VR0_PLANE1_PSI1 = 0x08
PSI_SEL_VR1_PLANE0_PSI0 = 0x10
PSI_SEL_VR1_PLANE0_PSI1 = 0x20
PSI_SEL_VR1_PLANE1_PSI0 = 0x40
PSI_SEL_VR1_PLANE1_PSI1 = 0x80
THROTTLER_PADDING_BIT = 0
THROTTLER_TEMP_EDGE_BIT = 1
THROTTLER_TEMP_HOTSPOT_BIT = 2
THROTTLER_TEMP_MEM_BIT = 3
THROTTLER_TEMP_VR_GFX_BIT = 4
THROTTLER_TEMP_VR_MEM0_BIT = 5
THROTTLER_TEMP_VR_MEM1_BIT = 6
THROTTLER_TEMP_VR_SOC_BIT = 7
THROTTLER_TEMP_LIQUID0_BIT = 8
THROTTLER_TEMP_LIQUID1_BIT = 9
THROTTLER_TEMP_PLX_BIT = 10
THROTTLER_TDC_GFX_BIT = 11
THROTTLER_TDC_SOC_BIT = 12
THROTTLER_PPT0_BIT = 13
THROTTLER_PPT1_BIT = 14
THROTTLER_PPT2_BIT = 15
THROTTLER_PPT3_BIT = 16
THROTTLER_FIT_BIT = 17
THROTTLER_PPM_BIT = 18
THROTTLER_APCC_BIT = 19
THROTTLER_COUNT = 20
FW_DSTATE_SOC_ULV_BIT = 0
FW_DSTATE_G6_HSR_BIT = 1
FW_DSTATE_G6_PHY_VDDCI_OFF_BIT = 2
FW_DSTATE_MP0_DS_BIT = 3
FW_DSTATE_SMN_DS_BIT = 4
FW_DSTATE_MP1_DS_BIT = 5
FW_DSTATE_MP1_WHISPER_MODE_BIT = 6
FW_DSTATE_SOC_LIV_MIN_BIT = 7
FW_DSTATE_SOC_PLL_PWRDN_BIT = 8
FW_DSTATE_MEM_PLL_PWRDN_BIT = 9
FW_DSTATE_OPTIMIZE_MALL_REFRESH_BIT = 10
FW_DSTATE_MEM_PSI_BIT = 11
FW_DSTATE_HSR_NON_STROBE_BIT = 12
FW_DSTATE_MP0_ENTER_WFI_BIT = 13
FW_DSTATE_SOC_ULV_MASK = (1 << FW_DSTATE_SOC_ULV_BIT          )
FW_DSTATE_G6_HSR_MASK = (1 << FW_DSTATE_G6_HSR_BIT           )
FW_DSTATE_G6_PHY_VDDCI_OFF_MASK = (1 << FW_DSTATE_G6_PHY_VDDCI_OFF_BIT )
FW_DSTATE_MP1_DS_MASK = (1 << FW_DSTATE_MP1_DS_BIT           )
FW_DSTATE_MP0_DS_MASK = (1 << FW_DSTATE_MP0_DS_BIT           )
FW_DSTATE_SMN_DS_MASK = (1 << FW_DSTATE_SMN_DS_BIT           )
FW_DSTATE_MP1_WHISPER_MODE_MASK = (1 << FW_DSTATE_MP1_WHISPER_MODE_BIT )
FW_DSTATE_SOC_LIV_MIN_MASK = (1 << FW_DSTATE_SOC_LIV_MIN_BIT      )
FW_DSTATE_SOC_PLL_PWRDN_MASK = (1 << FW_DSTATE_SOC_PLL_PWRDN_BIT    )
FW_DSTATE_MEM_PLL_PWRDN_MASK = (1 << FW_DSTATE_MEM_PLL_PWRDN_BIT    )
FW_DSTATE_OPTIMIZE_MALL_REFRESH_MASK = (1 << FW_DSTATE_OPTIMIZE_MALL_REFRESH_BIT    )
FW_DSTATE_MEM_PSI_MASK = (1 << FW_DSTATE_MEM_PSI_BIT    )
FW_DSTATE_HSR_NON_STROBE_MASK = (1 << FW_DSTATE_HSR_NON_STROBE_BIT    )
FW_DSTATE_MP0_ENTER_WFI_MASK = (1 << FW_DSTATE_MP0_ENTER_WFI_BIT    )
GFX_GPO_PACE_BIT = 0
GFX_GPO_DEM_BIT = 1
GFX_GPO_PACE_MASK = (1 << GFX_GPO_PACE_BIT)
GFX_GPO_DEM_MASK = (1 << GFX_GPO_DEM_BIT )
GPO_UPDATE_REQ_UCLKDPM_MASK = 0x1
GPO_UPDATE_REQ_FCLKDPM_MASK = 0x2
GPO_UPDATE_REQ_MALLHIT_MASK = 0x4
LED_DISPLAY_GFX_DPM_BIT = 0
LED_DISPLAY_PCIE_BIT = 1
LED_DISPLAY_ERROR_BIT = 2
RLC_PACE_TABLE_NUM_LEVELS = 16
SIENNA_CICHLID_UMC_CHANNEL_NUM = 16
NUM_I2C_CONTROLLERS = 16
I2C_CONTROLLER_ENABLED = 1
I2C_CONTROLLER_DISABLED = 0
MAX_SW_I2C_COMMANDS = 24
CMDCONFIG_STOP_BIT = 0
CMDCONFIG_RESTART_BIT = 1
CMDCONFIG_READWRITE_BIT = 2
CMDCONFIG_STOP_MASK = (1 << CMDCONFIG_STOP_BIT)
CMDCONFIG_RESTART_MASK = (1 << CMDCONFIG_RESTART_BIT)
CMDCONFIG_READWRITE_MASK = (1 << CMDCONFIG_READWRITE_BIT)
NUM_PIECE_WISE_LINEAR_DROOP_MODEL_VF_POINTS = 5
NUM_WM_RANGES = 4
WORKLOAD_PPLIB_DEFAULT_BIT = 0
WORKLOAD_PPLIB_FULL_SCREEN_3D_BIT = 1
WORKLOAD_PPLIB_POWER_SAVING_BIT = 2
WORKLOAD_PPLIB_VIDEO_BIT = 3
WORKLOAD_PPLIB_VR_BIT = 4
WORKLOAD_PPLIB_COMPUTE_BIT = 5
WORKLOAD_PPLIB_CUSTOM_BIT = 6
WORKLOAD_PPLIB_W3D_BIT = 7
WORKLOAD_PPLIB_COUNT = 8
TABLE_TRANSFER_OK = 0x0
TABLE_TRANSFER_FAILED = 0xFF
TABLE_PPTABLE = 0
TABLE_WATERMARKS = 1
TABLE_AVFS_PSM_DEBUG = 2
TABLE_AVFS_FUSE_OVERRIDE = 3
TABLE_PMSTATUSLOG = 4
TABLE_SMU_METRICS = 5
TABLE_DRIVER_SMU_CONFIG = 6
TABLE_ACTIVITY_MONITOR_COEFF = 7
TABLE_OVERDRIVE = 8
TABLE_I2C_COMMANDS = 9
TABLE_PACE = 10
TABLE_ECCINFO = 11
TABLE_COUNT = 12
UCLK_SWITCH_SLOW = 0
UCLK_SWITCH_FAST = 1
UCLK_SWITCH_DUMMY = 2
SMU_THERMAL_MINIMUM_ALERT_TEMP = 0
SMU_THERMAL_MAXIMUM_ALERT_TEMP = 255
SMU_TEMPERATURE_UNITS_PER_CENTIGRADES = 1000
SMU_FW_NAME_LEN = 0x24
SMU_DPM_USER_PROFILE_RESTORE = (1 << 0)
SMU_CUSTOM_FAN_SPEED_RPM = (1 << 1)
SMU_CUSTOM_FAN_SPEED_PWM = (1 << 2)
SMU_THROTTLER_PPT0_BIT = 0
SMU_THROTTLER_PPT1_BIT = 1
SMU_THROTTLER_PPT2_BIT = 2
SMU_THROTTLER_PPT3_BIT = 3
SMU_THROTTLER_SPL_BIT = 4
SMU_THROTTLER_FPPT_BIT = 5
SMU_THROTTLER_SPPT_BIT = 6
SMU_THROTTLER_SPPT_APU_BIT = 7
SMU_THROTTLER_TDC_GFX_BIT = 16
SMU_THROTTLER_TDC_SOC_BIT = 17
SMU_THROTTLER_TDC_MEM_BIT = 18
SMU_THROTTLER_TDC_VDD_BIT = 19
SMU_THROTTLER_TDC_CVIP_BIT = 20
SMU_THROTTLER_EDC_CPU_BIT = 21
SMU_THROTTLER_EDC_GFX_BIT = 22
SMU_THROTTLER_APCC_BIT = 23
SMU_THROTTLER_TEMP_GPU_BIT = 32
SMU_THROTTLER_TEMP_CORE_BIT = 33
SMU_THROTTLER_TEMP_MEM_BIT = 34
SMU_THROTTLER_TEMP_EDGE_BIT = 35
SMU_THROTTLER_TEMP_HOTSPOT_BIT = 36
SMU_THROTTLER_TEMP_SOC_BIT = 37
SMU_THROTTLER_TEMP_VR_GFX_BIT = 38
SMU_THROTTLER_TEMP_VR_SOC_BIT = 39
SMU_THROTTLER_TEMP_VR_MEM0_BIT = 40
SMU_THROTTLER_TEMP_VR_MEM1_BIT = 41
SMU_THROTTLER_TEMP_LIQUID0_BIT = 42
SMU_THROTTLER_TEMP_LIQUID1_BIT = 43
SMU_THROTTLER_VRHOT0_BIT = 44
SMU_THROTTLER_VRHOT1_BIT = 45
SMU_THROTTLER_PROCHOT_CPU_BIT = 46
SMU_THROTTLER_PROCHOT_GFX_BIT = 47
SMU_THROTTLER_PPM_BIT = 56
SMU_THROTTLER_FIT_BIT = 57