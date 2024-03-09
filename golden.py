import contextlib
import io
import logging
import os
import tempfile

import machine
import pytest
import translator

@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):

  # Установим уровень отладочного вывода на DEBUG
    caplog.set_level(logging.DEBUG)

    # Создаём временную папку для тестирования приложения.
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Готовим имена файлов для входных и выходных данных.
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.txt")
        target_code = os.path.join(tmpdirname, "target_code.o")
        target_data = os.path.join(tmpdirname, "target_data.o")

        # Записываем входные данные в файлы. Данные берутся из теста.
        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["in_source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["in_stdin"])

        # Запускаем транслятор и собираем весь стандартный вывод в переменную
        # stdout
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target_data, target_code)
            print("============================================================")
            machine.main(target_code, target_data, input_stream)

        # Выходные данные также считываем в переменные.
        with open(target_code, encoding="utf-8") as file:
            code = file.read()

        with open(target_data, encoding="utf-8") as file:
            data = file.read()

        # Проверяем, что ожидания соответствуют реальности.
        assert code == golden.out["out_code"]
        assert data == golden.out["out_data"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["out_log"]
