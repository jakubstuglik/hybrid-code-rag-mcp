1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
3. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
4. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
5. Persistent MCP server setup



Fixing document -> text payload in Qdrant small model in progress
Fixing document -> text payload in Qdrant big model to do


Coś jest nie tak z embedowaniem/dzieleniem na nodey? Przykład z weryfikacji payloadu a QDranta:

[EXAMPLE]
FILE: source/Common/TT_Ride/RideClasses.pas
LINES: 2326–2329
--- payload[text] (first 400 chars) ---
ng;
begin
result := self.Line_Number;
end;

function TRide.get_oneWay:
--- snippet from disk (first 400 chars) ---
function TRide.get_lineId: Integer;
begin
result := self.Line_ID;
end;