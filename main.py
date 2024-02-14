
import pandas as pd
# cargar datos
df_accesos_suscriptores = pd.read_csv("/Users/mauricio/Downloads/CARGO_FIJO_SUSCRIPTORES.csv", sep=";")
df_accesos_abonados = pd.read_csv("/Users/mauricio/Downloads/DEMANDA_ABONADOS.csv", sep=";")
df_trafico_suscriptores = pd.read_csv("/Users/mauricio/Downloads/TRAFICO_CARGO_FIJO.csv", sep=";")
df_trafico_abonados = pd.read_csv("/Users/mauricio/Downloads/TRAFICO_DEMANDA.csv", sep=";")

# procesar accesos
df_accesos = pd.concat([df_accesos_suscriptores, df_accesos_abonados], ignore_index=True)
df_accesos.rename(columns={"CANTIDAD_ABONADOS": "ACCESOS"}, inplace=True)
df_accesos = df_accesos.loc[df_accesos["MES_DEL_TRIMESTRE"] == 3]
df_accesos = df_accesos.fillna(0)
df_accesos["ACCESOS"] = df_accesos["ACCESOS"] + df_accesos["CANTIDAD_SUSCRIPTORES"]

#  tabla = pd.pivot_table(df_accesos, values="ACCESOS", index=["ANNO", "TRIMESTRE"], aggfunc="sum")

# procesar trafico
df_trafico = pd.concat([df_trafico_suscriptores, df_trafico_abonados])
df_trafico["TRAFICO"] = df_trafico["TRAFICO"].str.replace(",",".")
df_trafico["TRAFICO"] = df_trafico["TRAFICO"].astype(float)
#  tabla2 = pd.pivot_table(df_trafico, values="TRAFICO", index=["ANNO", "TRIMESTRE"], aggfunc="sum")

# i. calcular participaciones por dimension trafico y accesos
df_internet = pd.concat([df_accesos, df_trafico])
df_internet["TRAFICO_PERIODO"] = 0.0
df_internet["ACCESOS_PERIODO"] = 0
df_internet["PARTICIPACION_TRAFICO"] = 0.0
df_internet["PARTICIPACION_ACCESOS"] = 0.0
df_internet["PERIODO"] = df_internet["ANNO"].astype(str) + "-" + df_internet["TRIMESTRE"].astype(str)
# identifica en cual columna está periodo aunque # sabemos que está en la última columna, len(df.columns) - 1,
columna_periodo = df_internet.columns.get_loc("PERIODO")

periodo = "none"
for i in range(len(df_internet)):
    if periodo != df_internet.iat[i, columna_periodo]:
        periodo = df_internet.iat[i, columna_periodo]
        sub_conjunto = df_internet.loc[df_internet["PERIODO"] == periodo]  # genera subconjunto por periodo
        suma_trafico = sub_conjunto["TRAFICO"].sum()  # calcule tráfico total por periodo
        df_internet.loc[df_internet["PERIODO"] == periodo, "TRAFICO_PERIODO"] = suma_trafico
        suma_accesos = sub_conjunto["ACCESOS"].sum()  # calcule tráfico total por periodo
        df_internet.loc[df_internet["PERIODO"] == periodo, "ACCESOS_PERIODO"] = suma_accesos

columna_part_trafico = df_internet.columns.get_loc("PARTICIPACION_TRAFICO")
columna_part_accesos = df_internet.columns.get_loc("PARTICIPACION_ACCESOS")
for i in range(len(df_internet)):
    df_internet.iloc[i, columna_part_trafico] = round(df_internet.iloc[i]["TRAFICO"] /
                                                          df_internet.iloc[i]["TRAFICO_PERIODO"], 4)
    df_internet.iloc[i, columna_part_accesos] = round(df_internet.iloc[i]["ACCESOS"] /
                                                          df_internet.iloc[i]["ACCESOS_PERIODO"], 4)

participacion_trafico = pd.pivot_table(df_internet,
                                       values=["PARTICIPACION_TRAFICO"],
                                       index=["EMPRESA"],
                                       columns="PERIODO",
                                       aggfunc="sum",
                                       margins=True,  # presentar valores acumulados totales
                                       margins_name="Total")
participacion_trafico.reset_index(inplace=True)

participacion_accesos = pd.pivot_table(df_internet,
                                       values=["PARTICIPACION_ACCESOS"],
                                       index=["EMPRESA"],
                                       columns="PERIODO",
                                       aggfunc="sum",
                                       margins=True,  # presentar valores acumulados totales
                                       margins_name="Total",
                                       sort=True)
participacion_accesos.reset_index(inplace=True)


print(participacion_accesos)

# ii. Calcular trafico promedio mensual por acceso
df_internet = df_internet.loc[df_internet["ANNO"] > 2019]
trafico_promedio = pd.pivot_table(df_internet,
                                  values=["TRAFICO", "ACCESOS"],
                                  index=["ANNO", "TRIMESTRE"],
                                  aggfunc="sum")
trafico_promedio.reset_index(inplace=True)

trafico_promedio["TRAFICO_POR_ACCESO"] = (trafico_promedio.loc[:, "TRAFICO"] / (3 * trafico_promedio.loc[:, "ACCESOS"]))

trafico_promedio["TRAFICO_POR_ACCESO"] = round(trafico_promedio["TRAFICO_POR_ACCESO"] / 1024, 2)
print(trafico_promedio)

with pd.ExcelWriter('resul Mauricio Olaya.xlsx') as writer:
    participacion_accesos.to_excel(writer, sheet_name="i. Participacion accesos")
    participacion_trafico.to_excel(writer, sheet_name="i. Participacion trafico")
    trafico_promedio.to_excel(writer, sheet_name="ii. Trafico promedio")
