-- Emit booktabs tabular instead of pandoc longtable (avoids broken LT footers / overfull pages).

local function cell_latex(cell)
  local blocks = cell.contents
  if #blocks == 0 then
    return ""
  end
  return pandoc.write(pandoc.Pandoc(blocks), "latex"):gsub("\n+$", "")
end

local function col_align(align)
  if align == "AlignRight" then return "r"
  elseif align == "AlignCenter" then return "c"
  else return "l" end
end

function Table(tbl)
  local cols = {}
  for i = 1, #tbl.colspecs do
    cols[i] = col_align(tbl.colspecs[i][1])
  end
  local colspec = table.concat(cols, "")

  local lines = {}
  lines[#lines + 1] = "\\begin{table}[htbp]"
  lines[#lines + 1] = "\\centering"
  lines[#lines + 1] = "\\small"
  lines[#lines + 1] = string.format("\\begin{tabular}{%s}", colspec)
  lines[#lines + 1] = "\\toprule"

  if #tbl.head.rows > 0 then
    local row = tbl.head.rows[1]
    local cells = {}
    for _, c in ipairs(row.cells) do
      cells[#cells + 1] = cell_latex(c)
    end
    lines[#lines + 1] = table.concat(cells, " & ") .. " \\\\"
    lines[#lines + 1] = "\\midrule"
  end

  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      local cells = {}
      for _, c in ipairs(row.cells) do
        cells[#cells + 1] = cell_latex(c)
      end
      lines[#lines + 1] = table.concat(cells, " & ") .. " \\\\"
    end
  end

  lines[#lines + 1] = "\\bottomrule"
  lines[#lines + 1] = "\\end{tabular}"
  lines[#lines + 1] = "\\end{table}"

  return pandoc.RawBlock("latex", table.concat(lines, "\n"))
end
