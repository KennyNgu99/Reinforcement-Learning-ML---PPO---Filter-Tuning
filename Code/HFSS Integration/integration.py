import sys
import ScriptEnv
import clr
import warnings

warnings.filterwarnings(action="ignore")
sys.path.append("C:\Users\Lenovo Legion\PycharmProjects\pythonProject3\AnsysEM21.1\Win64")
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop.2021.1")
oProject = oDesktop.SetActiveProject("4thOrderChebyshev")
oDesign = oProject.SetActiveDesign("HFSSDesign1")
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab",
            [
                "NAME:PropServers",
                "LocalVariables"
            ],
            [
                "NAME:ChangedProps",
                [
                    "NAME:l1",
					"Value:="		, "(20.0 + 5.0045439302921295) mm"
                ]
            ]
        ]
    ])
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab",
            [
                "NAME:PropServers",
                "LocalVariables"
            ],
            [
                "NAME:ChangedProps",
                [
                    "NAME:l2",
					"Value:="		, "(18.0 + 13.0) mm"
                ]
            ]
        ]
    ])
oProject.Save()
oDesign.AnalyzeAll()
oModule = oDesign.GetModule("ReportSetup")
oModule.ExportToFile("S Parameter Plot 1", "C:/Users/Lenovo Legion/PycharmProjects/pythonProject3/S Parameter Plot 1.csv", False)