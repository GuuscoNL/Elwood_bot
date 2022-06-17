from table2ascii import table2ascii

players = []
for i in range(10):
   players.append(["GuuscoNL_"+str(i),"00:00:00"])
   
output = table2ascii(
                     header=["Player", "Time Played"],
                     body=players
                        )

print(output)