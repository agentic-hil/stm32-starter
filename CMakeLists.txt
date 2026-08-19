cmake_minimum_required(VERSION 3.21)

project(stm32-starter LANGUAGES C ASM)

set(MCU_FLAGS
    -mcpu=cortex-m4
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -mthumb
)

add_executable(stm32-starter
    firmware/src/main.c
    firmware/src/startup_stm32f446xx.S
)

target_compile_features(stm32-starter PRIVATE c_std_11)
target_compile_options(stm32-starter PRIVATE
    ${MCU_FLAGS}
    -ffreestanding
    -fdata-sections
    -ffunction-sections
    -Wall
    -Wextra
    -Wpedantic
    -Werror
    $<$<CONFIG:Debug>:-O0;-g3>
    $<$<CONFIG:Release>:-Os>
)

target_link_options(stm32-starter PRIVATE
    ${MCU_FLAGS}
    -nostdlib
    -T${CMAKE_CURRENT_SOURCE_DIR}/firmware/stm32f446re.ld
    -Wl,--gc-sections
    -Wl,-Map=${CMAKE_BINARY_DIR}/stm32-starter.map
    -Wl,--print-memory-usage
)

set_target_properties(stm32-starter PROPERTIES
    SUFFIX ".elf"
    LINK_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/firmware/stm32f446re.ld
)

add_custom_command(TARGET stm32-starter POST_BUILD
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:stm32-starter>
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:stm32-starter> ${CMAKE_BINARY_DIR}/stm32-starter.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:stm32-starter> ${CMAKE_BINARY_DIR}/stm32-starter.bin
)
