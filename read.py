import pdfplumber
import re

def extract_text_from_pdf(pdf_path):
    """
    Abre o PDF e extrai todo o texto das páginas.
    """
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Erro ao abrir o PDF {pdf_path}: {e}")
        return None
    return full_text

def clean_currency(value_str):
    """Converte string de moeda (R$ 1.234,56 ou 1.234,56) para float."""
    if not value_str: return 0.0
    clean = value_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0

def clean_number(num_str):
    """Converte string numérica (1.234,56) para float."""
    if not num_str: return 0.0
    clean = num_str.replace('.', '').replace(',', '.').strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0

def parse_cpfl_invoice(text):
    """
    Aplica Regex para extrair campos específicos da fatura CPFL.
    """
    data = {}

    nome_cpf_match = re.search(r"([A-Z\s]+)\s+CPF:\s*([\d\.-]+)", text)
    data['titular_nome'] = nome_cpf_match.group(1).strip() if nome_cpf_match else "Não encontrado"
    data['titular_documento'] = nome_cpf_match.group(2).strip() if nome_cpf_match else "Não encontrado"

    endereco_match = re.search(r"([A-Z0-9\s]+?)\s*CLASSIFICAÇÃO:\s*(.*?)\n(.*?)\n(\d{5}-\d{3}.*)", text)
    if endereco_match:
        data['endereco_completo'] = f"{endereco_match.group(1).strip()}, {endereco_match.group(3).strip()}, {endereco_match.group(4).strip()}"
        data['classificacao'] = endereco_match.group(2).strip()
    else:
        data['endereco_completo'] = "Não encontrado"
        data['classificacao'] = "Não encontrado"

    resumo_match = re.search(r"(\d{9})\s+INSTALAÇÃO\s+([A-Z]{3}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d,]+)", text)
    if resumo_match:
        data['numero_instalacao'] = resumo_match.group(1)
        data['mes_referencia'] = resumo_match.group(2)
        data['data_vencimento'] = resumo_match.group(3)
        data['valor_pagar'] = clean_currency(resumo_match.group(4))
    else:
        data['numero_instalacao'] = "Não encontrado"; data['mes_referencia'] = "Não encontrado"
        data['data_vencimento'] = "Não encontrado"; data['valor_pagar'] = 0.0

    tarifa_tusd = re.search(r"Energia Ativa Fornecida - TUSD.*?(?:kWh)\s+([\d,]+)", text)
    tarifa_te = re.search(r"Energia Ativa Fornecida - TE.*?(?:kWh)\s+([\d,]+)", text)
    data['tarifa_total_com_tributos'] = round(clean_number(tarifa_tusd.group(1)) + clean_number(tarifa_te.group(1)), 6) if tarifa_tusd and tarifa_te else 0.0
    data['tarifa_total_aneel'] = "Necessita cálculo deduzindo impostos"

    consumo_match = re.search(r"Energia Ativa Fornecida - TUSD.*?\s+([\d\.]+,\d+)\s+kWh", text)
    data['consumo_kwh'] = clean_number(consumo_match.group(1)) if consumo_match else 0.0

    saldo_match = re.search(r"Saldo em Energia da Instalação:.*?([\d\.,]+)\s*kWh", text)
    data['saldo_acumulado_kwh'] = clean_number(saldo_match.group(1)) if saldo_match else 0.0

    injetadas = re.findall(r"Energ Atv Inj.*?TUSD.*?\s+(\d+\.\d{3},\d+|\d+,\d+)\s+kWh", text)
    data['energia_compensada_kwh'] = sum(clean_number(val) for val in injetadas)

    total_op_match = re.search(r"Total Consolidado\s+([\d,]+)", text)
    data['total_operacoes'] = clean_currency(total_op_match.group(1)) if total_op_match else data['valor_pagar']

    cip_match = re.search(r"Contrib\. Custeio IP-CIP.*?\d{2}\s+([\d,]+)", text)
    data['contrib_ilum_publica'] = clean_currency(cip_match.group(1)) if cip_match else 0.0

    pis_cofins = re.search(r"PIS/COFINS\s+([\d,]+)%\s+([\d,]+)%", text)
    icms_match = re.search(r"Energia Ativa Fornecida - TUSD.*?kWh\s+[\d,]+\s+[\d,]+\s+[\d,]+\s+(\d{1,2},\d{2})", text)
    data['aliquotas'] = {
        'ICMS': icms_match.group(1) if icms_match else "0,00",
        'PIS': pis_cofins.group(1) if pis_cofins else "0,00",
        'COFINS': pis_cofins.group(2) if pis_cofins else "0,00"
    }

    linha_match = re.search(r"(\d{11,12}\s+\d{11,12}\s+\d{11,13}\s+\d{11,12})", text)
    data['linha_digitavel'] = linha_match.group(1) if linha_match else "Não encontrado"

    return data

def parse_cemig_invoice(text):
    """
    Aplica Regex para extrair campos específicos da fatura CEMIG.
    """
    data = {}

    nome_match = re.search(r"^([A-Z\s]+)\s+Referente", text, re.MULTILINE)
    data['titular_nome'] = nome_match.group(1).strip() if nome_match else "Não encontrado"

    doc_match = re.search(r"CPF\s+([\d\.-]+)", text)
    data['titular_documento'] = doc_match.group(1).strip() if doc_match else "Não encontrado"

    endereco_match = re.search(r"([A-Z\s0-9,]+)\s+[A-Z]{3}/\d{4}.*\n(.*)\n(\d{5}-\d{3}.*?)\s+NOTA", text)
    if endereco_match:
        data['endereco_completo'] = f"{endereco_match.group(1).strip()}, {endereco_match.group(2).strip()}, {endereco_match.group(3).strip()}"
    else:
        data['endereco_completo'] = "Não encontrado"

    valores_match = re.search(r"([A-Z]{3}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d,]+)", text)
    data['mes_referencia'] = valores_match.group(1) if valores_match else "Não encontrado"
    data['data_vencimento'] = valores_match.group(2) if valores_match else "Não encontrado"
    data['valor_pagar'] = clean_currency(valores_match.group(3)) if valores_match else 0.0

    # Captura o número da instalação ignorando possíveis datas de impressão na mesma linha
    inst_match = re.search(r"Nº DA INSTALAÇÃO.*?\n\d+\s+(\d+)", text)
    data['numero_instalacao'] = inst_match.group(1) if inst_match else "Não encontrado"

    class_match = re.search(r"(Residencial.*?Bifásico|Residencial.*?Monofásico|Residencial.*?Trifásico)", text, re.DOTALL)
    data['classificacao'] = class_match.group(1).replace('\n', ' ').strip() if class_match else "Não encontrado"

    tarifa_te_match = re.search(r"Energia Elétrica\s+kWh\s+\d+\s+([\d,]+)", text)
    data['tarifa_total_com_tributos'] = clean_number(tarifa_te_match.group(1)) if tarifa_te_match else 0.0
    
    tarifa_scee_match = re.search(r"Energia SCEE s/ ICMS\s+kWh\s+\d+\s+([\d,]+)", text)
    data['tarifa_total_aneel'] = clean_number(tarifa_scee_match.group(1)) if tarifa_scee_match else 0.0

    consumo_match = re.search(r"(?:JUL/23|[A-Z]{3}/\d{2})\s+(\d+)\s+", text)
    data['consumo_kwh'] = float(consumo_match.group(1)) if consumo_match else 0.0

    saldo_match = re.search(r"SALDO ATUAL DE GERAÇÃO:\s*([\d,]+)\s*kWh", text)
    data['saldo_acumulado_kwh'] = clean_number(saldo_match.group(1)) if saldo_match else 0.0

    comp1 = re.search(r"Energia compensada GD II.*?kWh\s+(\d+)", text)
    comp2 = re.search(r"Energia comp\. adicional.*?kWh\s+(\d+)", text)
    val1 = float(comp1.group(1)) if comp1 else 0.0
    val2 = float(comp2.group(1)) if comp2 else 0.0
    data['energia_compensada_kwh'] = val1 + val2

    data['total_operacoes'] = data['valor_pagar']

    cip_match = re.search(r"Contrib Ilum Publica Municipal\s+([\d,]+)", text)
    data['contrib_ilum_publica'] = clean_currency(cip_match.group(1)) if cip_match else 0.0

    data['aliquotas'] = {'ICMS': "0,00", 'PIS': "0,00", 'COFINS': "0,00"} 
    data['linha_digitavel'] = "Não encontrado"

    return data

def process_invoice(pdf_file, text_content):
    """Identifica a concessionária e aplica o parser correto."""
    if "CEMIG" in text_content.upper():
        return parse_cemig_invoice(text_content)
    elif "CPFL" in text_content.upper():
        return parse_cpfl_invoice(text_content)
    else:
        return None

def print_formated_data(data, filename):
    """
    Imprime os dados extraídos de forma organizada e estruturada no terminal, 
    atendendo aos requisitos de visualização do desafio.
    """
    print(f"\n===== DADOS EXTRAÍDOS: {filename} =====")
    print(f"Titular: {data.get('titular_nome', '')}")
    print(f"Documento: {data.get('titular_documento', '')}")
    print(f"Endereço Completo: {data.get('endereco_completo', '')}")
    print(f"Classificação da Instalação: {data.get('classificacao', '')}")
    print(f"Número da Instalação: {data.get('numero_instalacao', '')}")
    print(f"Valor a Pagar: R$ {data.get('valor_pagar', 0.0)}")
    print(f"Data de Vencimento: {data.get('data_vencimento', '')}")
    print(f"Mês de Referência: {data.get('mes_referencia', '')}")
    print(f"Tarifa total com tributos: {data.get('tarifa_total_com_tributos', '')}")
    print(f"Tarifa total Aneel: {data.get('tarifa_total_aneel', '')}")
    print(f"Consumo (kWh): {data.get('consumo_kwh', 0.0)}")
    print(f"Saldo acumulado (kWh): {data.get('saldo_acumulado_kwh', 0.0)}")
    print(f"Somatório energias compensadas: {data.get('energia_compensada_kwh', 0.0)}")
    print(f"Total das Operações: R$ {data.get('total_operacoes', 0.0)}")
    print(f"Contribuição Iluminação Pública: R$ {data.get('contrib_ilum_publica', 0.0)}")
    print(f"Linha Digitável: {data.get('linha_digitavel', '')}")
    
    aliquotas = data.get('aliquotas', {})
    print(f"ICMS: {aliquotas.get('ICMS', '0,00')}%")
    print(f"PIS: {aliquotas.get('PIS', '0,00')}%")
    print(f"COFINS: {aliquotas.get('COFINS', '0,00')}%\n")

def main():
    # Definição dos arquivos de fatura a serem processados na rotina
    faturas = ["fatura_cpfl.pdf", "fatura_cemig.pdf", "fatura_cemig_convencional.pdf"]
    
    for pdf_file in faturas:
        text_content = extract_text_from_pdf(pdf_file)
        
        if text_content:
            extracted_data = process_invoice(pdf_file, text_content)
            if extracted_data:
                print_formated_data(extracted_data, pdf_file)
            else:
                print(f"\n[{pdf_file}] Concessionária não reconhecida.")
        else:
            print(f"\nArquivo {pdf_file} não encontrado ou erro de leitura.")

if __name__ == "__main__":
    main()